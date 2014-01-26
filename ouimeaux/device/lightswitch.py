from .switch import Switch

class LightSwitch(Switch):

    def __repr__(self):
        return '<WeMo LightSwitch "{name}">'.format(name=self.name)
