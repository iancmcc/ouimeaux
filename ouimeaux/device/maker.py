from datetime import datetime
from .switch import Switch
from ouimeaux.device import Device
from xml.etree import cElementTree as et


class Maker(Device):

    def __repr__(self):
        return '<WeMo Maker "{name}">'.format(name=self.name)

    @property
    def maker_attribs(self):
        makerresp = self.deviceevent.GetAttributes().get('attributeList')
        makerresp = "<attributes>" + makerresp + "</attributes>"
        makerresp = makerresp.replace("&gt;",">")
        makerresp = makerresp.replace("&lt;","<")
        attributes = et.fromstring(makerresp)
        for attribute in attributes:
            if attribute[0].text == "Switch":
            	state = attribute[1].text
            elif attribute[0].text == "Sensor":
            	sensorstate = attribute[1].text
            elif attribute[0].text == "SwitchMode":
            	switchmode = attribute[1].text
            elif attribute[0].text == "SensorPresent":
            	hassensor = attribute[1].text
        return { 'state' : state,
        		 'sensorstate' : int(sensorstate),
        		 'switchmode' : int(switchmode),
        		 'hassensor' : int(hassensor)}

    @property
    def sensor_state(self):
        return self.maker_attribs['sensorstate']
        
    @property
    def switch_mode(self):
    	return self.maker_attribs['switchmode']
    
    @property
    def has_sensor(self):
    	return self.maker_attribs['hassensor']
