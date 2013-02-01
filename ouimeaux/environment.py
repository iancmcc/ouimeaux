import logging

import gevent

from ouimeaux.motion import Motion
from ouimeaux.switch import Switch
from ouimeaux.upnp import UPnP


_NOOP = lambda *x: None
log = logging.getLogger(__name__)


class StopBroadcasting(Exception): pass
class UnknownDevice(Exception): pass


class Environment(object):
    def __init__(self, switch_callback=_NOOP, motion_callback=_NOOP):
        self.upnp = UPnP(self._found_device)
        self._switch_callback = switch_callback
        self._motion_callback = motion_callback
        self.switches = {}
        self.motions = {}

    def discover(self, seconds=10):
        log.info("Beginning discovery of devices")
        self.upnp.server.set_spawn(2)
        self.upnp.server.start()
        with gevent.Timeout(seconds, StopBroadcasting) as timeout:
            try:
                try:
                    while True:
                        self.upnp.broadcast()
                        gevent.sleep(1)
                except Exception as e:
                    raise StopBroadcasting(e)
            except StopBroadcasting:
                self.upnp.server.stop()
                return

    def _found_device(self, address, headers):
        usn = headers['usn']
        if usn.startswith('uuid:Socket'):
            switch = Switch(headers['location'])
            self.switches[switch.name] = switch
            self._switch_callback(switch)
        elif usn.startswith('uuid:Sensor'):
            motion = Motion(headers['location'])
            self.motions[motion.name] = motion
            self._motion_callback(motion)

    def list_switches(self):
        return self.switches.keys()

    def list_motions(self):
        return self.motions.keys()

    def get_switch(self, name):
        try:
            return self.switches[name]
        except KeyError:
            raise UnknownDevice(name)

    def get_motion(self, name):
        try:
            return self.motions[name]
        except KeyError:
            raise UnknownDevice(name)


if __name__ == "__main__":
    # Use with python -i
    environment = Environment()
