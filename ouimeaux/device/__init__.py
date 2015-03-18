import logging
from urlparse import urlparse

from .api.service import Service
from .api.xsd import device as deviceParser
from ..utils import requests_get


log = logging.getLogger(__name__)


class DeviceUnreachable(Exception): pass
class UnknownService(Exception): pass


class Device(object):
    def __init__(self, url):
        self._state = None
        base_url = url.rsplit('/', 1)[0]
        self.host = urlparse(url).hostname
        #self.port = urlparse(url).port
        xml = requests_get(url)
        self._config = deviceParser.parseString(xml.content).device
        sl = self._config.serviceList
        self.services = {}
        for svc in sl.service:
            svcname = svc.get_serviceType().split(':')[-2]
            if svcname != "deviceevent":
                service = Service(svc, base_url)
                service.eventSubURL = base_url + svc.get_eventSubURL()
                self.services[svcname] = service
                setattr(self, svcname, service)

    def _update_state(self, value):
        self._state = int(value)

    def get_state(self, force_update=False):
        """
        Returns 0 if off and 1 if on.
        """
        if force_update or self._state is None:
            return int(self.basicevent.GetBinaryState()['BinaryState'])
        return self._state

    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        if 'register_listener' in odict:
            del odict['register_listener']
        return odict

    def get_service(self, name):
        try:
            return self.services[name]
        except KeyError:
            raise UnknownService(name)

    def list_services(self):
        return self.services.keys()

    def ping(self):
        try:
            self.get_state()
        except Exception:
            raise DeviceUnreachable(self)

    def explain(self):
        for name, svc in self.services.iteritems():
            print name
            print '-' * len(name)
            for aname, action in svc.actions.iteritems():
                print "  %s(%s)" % (aname, ', '.join(action.args))
            print

    @property
    def model(self):
        return self._config.get_modelDescription()

    @property
    def name(self):
        return self._config.get_friendlyName()

    @property
    def serialnumber(self):
        return self._config.get_serialNumber()


def test():
    device = Device("http://10.42.1.102:49152/setup.xml")
    print device.get_service('basicevent').SetBinaryState(BinaryState=1)


if __name__ == "__main__":
    test()

