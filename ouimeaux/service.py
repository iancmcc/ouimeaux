from xml.etree import cElementTree as et

import requests

from ouimeaux.device import REQUEST_TEMPLATE
from ouimeaux.xsd import service as serviceParser


class Service(object):
    def __init__(self, service, base_url):
        self._base_url = base_url.rstrip('/')
        self._config = service
        url = '%s/%s' % (base_url, service.get_SCPDURL().strip('/'))
        xml = requests.get(url)
        self._svc_config = serviceParser.parseString(xml.content).actionList
        self.actions = {a.get_name(): a for a in self._svc_config.get_action()}

    @property
    def hostname(self):
        return self._base_url.split('/')[-1]

    @property
    def controlURL(self):
        return '%s/%s' % (self._base_url, self._config.get_controlURL().strip('/'))

    @property
    def serviceType(self):
        return self._config.get_serviceType()

    def __getattr__(self, attr):
        if attr not in self.actions:
            raise AttributeError(attr)

        def _act(**kwargs):
            arglist = '\n'.join('<{0}>{1}</{0}>'.format(arg, value) for arg, value in kwargs.iteritems())
            body = REQUEST_TEMPLATE.format(
                action=attr,
                service=self.serviceType,
                args=arglist
            )
            headers = {
                'Content-Type': 'text/xml',
                'SOAPACTION': '"%s#%s"' % (self.serviceType, attr)
            }
            response = requests.post(self.controlURL, body.strip(), headers=headers)
            d = {}
            for r in et.fromstring(response.content).getchildren()[0].getchildren()[0].getchildren():
                d[r.tag] = r.text
            return d

        _act.__name__ = attr
        return _act
