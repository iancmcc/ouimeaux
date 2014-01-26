import logging

import gevent
from gevent import socket
from gevent.server import DatagramServer

from ouimeaux.utils import get_ip_address
from pysignals import receiver
from ouimeaux.signals import discovered


log = logging.getLogger(__name__)


class UPnPLoopbackException(Exception):
    """
    Using loopback interface as callback IP.
    """


class UPnP(object):
    """
    Makes M-SEARCH requests, filters out non-WeMo responses, and dispatches
    signals with the results.
    """
    def __init__(self, mcast_ip='239.255.255.250', mcast_port=1900, bind=None):
        if bind is None:
            host = get_ip_address()
            if host.startswith('127.'):
                raise UPnPLoopbackException("Using %s as a callback IP for "
                                            "discovery will not be successful.")
            port = 54321
            bind = '{0}:{1}'.format(host, port)
        self.bind = bind
        self.mcast_ip = mcast_ip
        self.mcast_port = mcast_port
        self.clients = {}

    def _response_received(self, message, address):
        log.debug("Received a response from {0}:{1}".format(*address))
        if address[0] not in self.clients:
            lines = message.splitlines()
            lines.pop(0) # HTTP status
            headers = {}
            for line in lines:
                try:
                    header, value = line.split(":", 1)
                    headers[header.lower()] = value.strip()
                except ValueError:
                    continue
            if (headers.get('x-user-agent', None) == 'redsonic'):
                log.debug("Found WeMo at {0}:{1}".format(*address))
                self.clients[address[0]] = headers
                gevent.spawn(discovered.send, self, address=address,
                        headers=headers)

    @property
    def server(self):
        """
        UDP server to listen for responses.
        """
        server = getattr(self, "_server", None)
        if server is None:
            log.debug("Binding datagram server to %s", self.bind)
            server = DatagramServer(self.bind, self._response_received)
            self._server = server
        return server

    def broadcast(self):
        """
        Send a multicast M-SEARCH request asking for devices to report in.
        """
        log.debug("Broadcasting M-SEARCH to %s:%s", self.mcast_ip, self.mcast_port)
        request = '\r\n'.join(("M-SEARCH * HTTP/1.1",
                               "HOST:{mcast_ip}:{mcast_port}",
                               "ST:upnp:rootdevice",
                               "MX:2",
                               'MAN:"ssdp:discover"',
                               "", "")).format(**self.__dict__)
        self.server.sendto(request, (self.mcast_ip, self.mcast_port))


def test():
    logging.basicConfig(level=logging.DEBUG)

    @receiver(discovered)
    def handler(sender, **kwargs):
        print "I GOT ONE"
        print kwargs['address'], kwargs['headers']

    upnp = UPnP()
    upnp.server.set_spawn(1)
    upnp.server.start()
    log.debug("Started server, listening for responses")
    with gevent.Timeout(2, KeyboardInterrupt):
        while True:
            try:
                upnp.broadcast()
                gevent.sleep(2)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    test()
