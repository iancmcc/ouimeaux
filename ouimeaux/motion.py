from ouimeaux.device import Device

class Motion(Device):

    def __repr__(self):
        return '<WeMo Motion "{name}">'.format(name=self.name)
