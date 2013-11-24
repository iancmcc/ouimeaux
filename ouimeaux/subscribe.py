from collections import defaultdict
import logging
from xml.etree import cElementTree
from functools import partial

import requests
import gevent
from gevent import socket
from gevent.wsgi import WSGIServer

from .utils import get_ip_address


log = logging.getLogger(__name__)

NS = "{urn:schemas-upnp-org:event-1-0}"
SUCCESS = '<html><body><h1>200 OK</h1></body></html>'


class SubscriptionRegistry(object):
    def __init__(self):
        self._devices = {}
        self._callbacks = defaultdict(list)

    def register(self, device):
        log.info("Subscribing to basic events from %r", (device,))
        # Provide a function to register a callback when the device changes state
        device.register_listener = partial(self.on, device, 'BinaryState')
        self._devices[device.host] = device
        self._resubscribe(device.basicevent.eventSubURL)

    def _resubscribe(self, url, sid=None):
        headers = {'TIMEOUT': 'infinite'}
        if sid is not None:
            headers['SID'] = sid
        else:
            host = get_ip_address()
            headers.update({
                "CALLBACK": '<http://%s:8989>' % host,
                "NT": "upnp:event"
            })

        response = requests.request(method="SUBSCRIBE", url=url,
                                    headers=headers)

        timeout = int(response.headers['timeout'].replace('Second-', ''))
        sid = response.headers['sid']
        gevent.spawn_later(timeout, self._resubscribe, url, sid)

    def _handle(self, environ, start_response):
        device = self._devices[environ['REMOTE_ADDR']]
        doc = cElementTree.parse(environ['wsgi.input'])
        for propnode in doc.findall('./{0}property'.format(NS)):
            for property_ in propnode.getchildren():
                self._event(device, property_.tag, property_.text)
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
            server = WSGIServer(('', 8989), self._handle)
            self._server = server
        return server

