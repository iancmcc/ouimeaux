import gevent

from ouimeaux.device import Device


class Switch(Device):

    def set_state(self, state):
        """
        Set the state of this device to on or off.
        """
        self.basicevent.SetBinaryState(BinaryState=int(state))
        self._state = int(state)

    def off(self):
        """
        Turn this device off. If already off, will return "Error".
        """
        return self.set_state(0)

    def on(self):
        """
        Turn this device on. If already on, will return "Error".
        """
        return self.set_state(1)

    def toggle(self):
        """
        Toggle the switch's state.
        """
        return self.set_state(not self.get_state())

    def blink(self, delay=1):
        """
        Toggle the switch once, then again after a delay (in seconds).
        """
        self.toggle()
        gevent.spawn_later(delay, self.toggle)

    def __repr__(self):
        return '<WeMo Switch "{name}">'.format(name=self.name)
