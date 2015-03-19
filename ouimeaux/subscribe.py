from collections import defaultdict
import logging
from xml.etree import cElementTree
from functools import partial

import gevent
from gevent.wsgi import WSGIServer

from ouimeaux.utils import get_ip_address, requests_request
from ouimeaux.device.insight import Insight
from ouimeaux.device.maker import Maker
from ouimeaux.signals import subscription


log = logging.getLogger(__name__)

NS = "{urn:schemas-upnp-org:event-1-0}"
SUCCESS = '<html><body><h1>200 OK</h1></body></html>'


class SubscriptionRegistry(object):
    def __init__(self):
        self._devices = {}
        self._callbacks = defaultdict(list)

    def register(self, device):
        if not device:
            log.error("Received an invalid device: %r", device)
            return
        log.info("Subscribing to basic events from %r", device)
        # Provide a function to register a callback when the device changes
        # state
        device.register_listener = partial(self.on, device, 'BinaryState')
        self._devices[device.host] = device
        self._resubscribe(device.basicevent.eventSubURL)

    def _resubscribe(self, url, sid=None):
        headers = {'TIMEOUT': 'Second-%d' % 1800}
        if sid is not None:
            headers['SID'] = sid
        else:
            host = get_ip_address()
            headers.update({
                "CALLBACK": '<http://%s:8989>' % host,
                "NT": "upnp:event"
            })
        response = requests_request(method="SUBSCRIBE", url=url,
                                    headers=headers)
        if response.status_code == 412 and sid:
            # Invalid subscription ID. Send an UNSUBSCRIBE for safety and
            # start over.
            requests_request(method='UNSUBSCRIBE', url=url,
                             headers={'SID': sid})
            return self._resubscribe(url)
        timeout = int(response.headers.get('timeout', '1801').replace(
            'Second-', ''))
        sid = response.headers.get('sid', sid)
        gevent.spawn_later(int(timeout * 0.75), self._resubscribe, url, sid)

    def _handle(self, environ, start_response):
        device = self._devices.get(environ['REMOTE_ADDR'])
        if device is not None:
            data = environ['wsgi.input'].read()
            # trim garbage from end, if any
            data = data.split("\n\n")[0]
            doc = cElementTree.fromstring(data)
            for propnode in doc.findall('./{0}property'.format(NS)):
                for property_ in propnode.getchildren():
                    text = property_.text
                    if isinstance(device, Insight) and property_.tag=='BinaryState':
                        text = text.split('|')[0]
                    subscription.send(device, type=property_.tag, value=text)
                    self._event(device, property_.tag, text)
        start_response('200 OK', [
            ('Content-Type', 'text/html'),
            ('Content-Length', len(SUCCESS)),
            ('Connection', 'close')
        ])
        yield SUCCESS

    def _event(self, device, type_, value):
        for t, callback in self._callbacks.get(device, ()):
            if t == type_:
                callback(value)

    def on(self, device, type, callback):
        self._callbacks[device].append((type, callback))

    @property
    def server(self):
        """
        UDP server to listen for responses.
        """
        server = getattr(self, "_server", None)
        if server is None:
            server = WSGIServer(('', 8989), self._handle, log=None)
            self._server = server
        return server

