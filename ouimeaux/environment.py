import logging

import gevent

from ouimeaux.motion import Motion
from ouimeaux.subscribe import SubscriptionRegistry
from ouimeaux.switch import Switch
from ouimeaux.upnp import UPnP


_NOOP = lambda *x: None
log = logging.getLogger(__name__)

reqlog = logging.getLogger("requests")
reqlog.disabled = True


class StopBroadcasting(Exception):
    pass


class UnknownDevice(Exception):
    pass


class Environment(object):
    def __init__(self, switch_callback=_NOOP, motion_callback=_NOOP,
                 with_subscribers=True):
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
        """
        self.upnp = UPnP(self._found_device)
        self.registry = SubscriptionRegistry()
        self._with_subscribers = with_subscribers
        self._switch_callback = switch_callback
        self._motion_callback = motion_callback
        self._switches = {}
        self._motions = {}

    def start(self):
        """
        Start the server(s) necessary to receive information from devices.
        """
        # Start the server to listen to new devices
        self.upnp.server.set_spawn(2)
        self.upnp.server.start()

        if self._with_subscribers:
            # Start the server to listen to events
            self.registry.server.set_spawn(2)
            self.registry.server.start()

    def wait(self):
        """
        Wait for events.
        """
        try:
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

    def _found_device(self, address, headers):
        log.info("Found device at %s" % (address,))
        usn = headers['usn']
        if usn.startswith('uuid:Socket'):
            klass = Switch
            callback = self._switch_callback
            registry = self._switches
        elif usn.startswith('uuid:Sensor'):
            klass = Motion
            callback = self._motion_callback
            registry = self._motions
        else:
            return
        device = klass(headers['location'])
        registry[device.name] = device
        if self._with_subscribers:
            self.registry.register(device)
            self.registry.on(device, 'BinaryState',
                             device._update_state)
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


if __name__ == "__main__":
    # Use with python -i
    environment = Environment()
