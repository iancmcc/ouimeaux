import logging
from xml.etree import cElementTree as et


from ...utils import requests_get, requests_post
from .xsd import service as serviceParser


log = logging.getLogger(__name__)

REQUEST_TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
 <s:Body>
  <u:{action} xmlns:u="{service}">
   {args}
  </u:{action}>
 </s:Body>
</s:Envelope>
"""


class Action(object):
    def __init__(self, service, action_config):
        self._action_config = action_config
        self.name = action_config.get_name()
        self.serviceType = service.serviceType
        self.controlURL = service.controlURL
        self.args = {}
        self.headers = {
            'Content-Type': 'text/xml',
            'SOAPACTION': '"%s#%s"' % (self.serviceType, self.name)
        }
        arglist = action_config.get_argumentList()
        if arglist is not None:
            for arg in arglist.get_argument():
                name = arg.get_name()
                if name:
                    # TODO: Get type instead of setting 0
                    self.args[arg.get_name()] = 0

    def __call__(self, **kwargs):
        arglist = '\n'.join('<{0}>{1}</{0}>'.format(arg, value)
                            for arg, value in kwargs.iteritems())
        body = REQUEST_TEMPLATE.format(
            action=self.name,
            service=self.serviceType,
            args=arglist
        )
        response = requests_post(self.controlURL, body.strip(), headers=self.headers)
        d = {}
        for r in et.fromstring(response.content).getchildren()[0].getchildren()[0].getchildren():
            d[r.tag] = r.text
        return d

    def __repr__(self):
        return "<Action %s(%s)>" % (self.name, ", ".join(self.args))


class Service(object):
    """
    Represents an instance of a service on a device.
    """

    def __init__(self, service, base_url):
        self._base_url = base_url.rstrip('/')
        self._config = service
        url = '%s/%s' % (base_url, service.get_SCPDURL().strip('/'))
        xml = requests_get(url)
        self.actions = {}
        self._svc_config = serviceParser.parseString(xml.content).actionList
        for action in self._svc_config.get_action():
            act = Action(self, action)
            name = action.get_name()
            self.actions[name] = act
            setattr(self, name, act)

    @property
    def hostname(self):
        return self._base_url.split('/')[-1]

    @property
    def controlURL(self):
        return '%s/%s' % (self._base_url,
                          self._config.get_controlURL().strip('/'))

    @property
    def serviceType(self):
        return self._config.get_serviceType()
