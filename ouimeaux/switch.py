
from ouimeaux.device import Device


class Switch(Device):

    def get_state(self):
        return int(self.get_service('basicevent').GetBinaryState()['BinaryState'])

    def set_state(self, state):
        self.get_service('basicevent').SetBinaryState(BinaryState=int(state))

    def off(self):
        return self.set_state(0)

    def on(self):
        return self.set_state(1)

    def __str__(self):
        return '<WeMo Switch "{name}">'.format(name=self.name)

