from datetime import datetime
from ouimeaux.device import Device
from xml.etree import ElementTree as et


class Maker(Device):

    def __repr__(self):
        return '<WeMo Maker "{name}">'.format(name=self.name)

    def get_state(self, force_update=False):
        """
        Returns 0 if off and 1 if on.
        """
        # The base implementation using GetBinaryState doesn't work for Maker (always returns 0).
        # So pull the switch state from the atrributes instead
        if force_update or self._state is None:
            return(int(self.maker_attribs.get('switchstate',0)))
        return self._state

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

    @property
    def maker_attribs(self):
        makerresp = self.deviceevent.GetAttributes().get('attributeList')
        makerresp = "<attributes>" + makerresp + "</attributes>"
        makerresp = makerresp.replace("&gt;",">")
        makerresp = makerresp.replace("&lt;","<")
        attributes = et.fromstring(makerresp)
        for attribute in attributes:
            if attribute[0].text == "Switch":
              switchstate = attribute[1].text
            elif attribute[0].text == "Sensor":
              sensorstate = attribute[1].text
            elif attribute[0].text == "SwitchMode":
            	switchmode = attribute[1].text
            elif attribute[0].text == "SensorPresent":
            	hassensor = attribute[1].text
        return { 'switchstate' : int(switchstate),
             'sensorstate' : int(sensorstate),
        		 'switchmode' : int(switchmode),
        		 'hassensor' : int(hassensor)}

    @property
    def switch_state(self):
        return self.maker_attribs['switchstate']

    @property
    def sensor_state(self):
        return self.maker_attribs['sensorstate']

    @property
    def switch_mode(self):
    	return self.maker_attribs['switchmode']

    @property
    def has_sensor(self):
    	return self.maker_attribs['hassensor']
