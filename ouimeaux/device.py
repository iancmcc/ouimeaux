import logging

import requests

from ouimeaux.service import Service
from ouimeaux.xsd import device as deviceParser


log = logging.getLogger(__name__)


class Device(object):
    def __init__(self, url):
        base_url = url.rsplit('/', 1)[0]
        xml = requests.get(url)
        self._config = deviceParser.parseString(xml.content).device
        sl = self._config.serviceList
        self.services = {}
        for svc in sl.service:
            svcname = svc.get_serviceType().split(':')[-2]
            self.services[svcname] = Service(svc, base_url)

    def get_service(self, name):
        return self.services.get(name, None)

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
    print device.get_service('basicevent').SetBinaryState(BinaryState=0)


if __name__ == "__main__":
    test()

