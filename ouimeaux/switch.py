from ouimeaux.device import Device


class Switch(Device):

    def get_state(self):
        """
        Returns 0 if off and 1 if on.
        """
        return int(self.basicevent.GetBinaryState()['BinaryState'])

    def set_state(self, state):
        """
        Set the state of this device to on or off.
        """
        self.basicevent.SetBinaryState(BinaryState=int(state))

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

    def __repr__(self):
        return '<WeMo Switch "{name}">'.format(name=self.name)

