import logging

import gevent
import requests

from ouimeaux.config import get_cache, WemoConfiguration
from ouimeaux.device import DeviceUnreachable
from ouimeaux.device.switch import Switch
from ouimeaux.device.insight import Insight
from ouimeaux.device.maker import Maker
from ouimeaux.device.lightswitch import LightSwitch
from ouimeaux.device.motion import Motion
from ouimeaux.device.bridge import Bridge
from ouimeaux.discovery import UPnP
from ouimeaux.signals import discovered, devicefound
from ouimeaux.subscribe import SubscriptionRegistry
from ouimeaux.utils import matcher


_NOOP = lambda *x: None
log = logging.getLogger(__name__)

reqlog = logging.getLogger("requests")
reqlog.disabled = True


class StopBroadcasting(Exception):
    pass


class UnknownDevice(Exception):
    pass

class Environment(object):
    def __init__(self, switch_callback=_NOOP, motion_callback=_NOOP, bridge_callback=_NOOP,
                 maker_callback=_NOOP, with_discovery=True, with_subscribers=True, with_cache=None, 
                 bind=None, config_filename=None):
        """
        Create a WeMo environment.

        @param switch_callback: A function to be called when a new switch is
                                discovered.
        @type switch_callback:  function
        @param motion_callback: A function to be called when a new motion is
                                discovered.
        @type motion_callback:  function
        @param with_subscribers: Whether to register for events with discovered
                                devices.
        @type with_subscribers: bool
        @param bind: ip:port to which to bind the response server.
        @type bind: str
        """
        self._config = WemoConfiguration(filename=config_filename)
        self.upnp = UPnP(bind=bind or self._config.bind)
        discovered.connect(self._found_device, self.upnp)
        self.registry = SubscriptionRegistry()
        if with_cache is None:
            with_cache = (self._config.cache if self._config.cache is not None else True)
        self._with_cache = with_cache
        self._with_discovery = with_discovery
        self._with_subscribers = with_subscribers
        self._switch_callback = switch_callback
        self._motion_callback = motion_callback
        self._bridge_callback = bridge_callback
        self._maker_callback = maker_callback
        self._switches = {}
        self._motions = {}
        self._bridges = {}
        self._makers = {}
        self.devices = {}

    def __iter__(self):
        return self.devices.itervalues()

    def start(self):
        """
        Start the server(s) necessary to receive information from devices.
        """
        if self._with_cache:
            with get_cache() as c:
                for dev in c.devices:
                    self._process_device(dev, cache=False)

        if self._with_discovery:
            # Start the server to listen to new devices
            self.upnp.server.set_spawn(2)
            self.upnp.server.start()

        if self._with_subscribers:
            # Start the server to listen to events
            self.registry.server.set_spawn(2)
            self.registry.server.start()

    def wait(self, timeout=None):
        """
        Wait for events.
        """
        try:
            if timeout:
                gevent.sleep(timeout)
            else:
                while True:
                    gevent.sleep(1000)
        except (KeyboardInterrupt, SystemExit, Exception):
            pass

    def discover(self, seconds=2):
        """
        Discover devices in the environment.

        @param seconds: Number of seconds to broadcast requests.
        @type seconds: int
        """
        log.info("Discovering devices")
        with gevent.Timeout(seconds, StopBroadcasting) as timeout:
            try:
                try:
                    while True:
                        self.upnp.broadcast()
                        gevent.sleep(1)
                except Exception as e:
                    raise StopBroadcasting(e)
            except StopBroadcasting:
                return

    def _found_device(self, sender, **kwargs):
        address = kwargs['address']
        headers = kwargs['headers']
        usn = headers['usn']
        if usn.startswith('uuid:Socket'):
            klass = Switch
        elif usn.startswith('uuid:Lightswitch'):
            klass = LightSwitch
        elif usn.startswith('uuid:Insight'):
            klass = Insight
        elif usn.startswith('uuid:Sensor'):
            klass = Motion
        elif usn.startswith('uuid:Bridge'):
            klass = Bridge
        elif usn.startswith('uuid:Maker'):
        	klass = Maker
        else:
            log.info("Unrecognized device type. USN={0}".format(usn))
            return
        device = klass(headers['location'])
        log.info("Found device %r at %s" % (device, address))
        self._process_device(device)

    def _process_device(self, device, cache=None):
        if isinstance(device, Switch):
            callback = self._switch_callback
            registry = self._switches
        elif isinstance(device, Motion):
            callback = self._motion_callback
            registry = self._motions
        elif isinstance(device, Bridge):
            callback = self._bridge_callback
            registry = self._bridges
            for light in device.Lights:
                log.info("Found light \"%s\" connected to \"%s\"" % (light, device.name))
        elif isinstance(device, Maker):
            callback = self._maker_callback
            registry = self._makers
        else:
            return
        self.devices[device.name] = device
        registry[device.name] = device
        if self._with_subscribers:
            self.registry.register(device)
            self.registry.on(device, 'BinaryState',
                             device._update_state)
        try:
            if isinstance(device, Bridge):
                pass
            else:
                device.ping()
        except DeviceUnreachable:
            return
        else:
            if cache if cache is not None else self._with_cache:
                with get_cache() as c:
                    c.add_device(device)
        devicefound.send(device)
        callback(device)

    def list_switches(self):
        """
        List switches discovered in the environment.
        """
        return self._switches.keys()

    def list_motions(self):
        """
        List motions discovered in the environment.
        """
        return self._motions.keys()
        
    def list_makers(self):
    	"""
        List makers discovered in the environment.
        """
        return self._makers.keys()

    def list_bridges(self):
        """
        List bridges discovered in the environment.
        """
        return self._bridges.keys()

    def get(self, name):
        alias = self._config.aliases.get(name)
        if alias:
            matches = lambda x: x == alias
        elif name:
            matches = matcher(name)
        else:
            matches = _NOOP
        for k in self.devices:
            if matches(k):
                return self.devices[k]
        else:
            raise UnknownDevice(name)

    def get_switch(self, name):
        """
        Get a switch by name.
        """
        try:
            return self._switches[name]
        except KeyError:
            raise UnknownDevice(name)

    def get_motion(self, name):
        """
        Get a motion by name.
        """
        try:
            return self._motions[name]
        except KeyError:
            raise UnknownDevice(name)

    def get_bridge(self, name):
        """
        Get a bridge by name.
        """
        try:
            return self._bridges[name]
        except KeyError:
            raise UnknownDevice(name)

    def get_maker(self, name):
        """
        Get a maker by name.
        """
        try:
            return self._makers[name]
        except KeyError:
            raise UnknownDevice(name)


if __name__ == "__main__":
    # Use with python -i
    environment = Environment()
