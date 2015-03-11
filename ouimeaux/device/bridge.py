from ouimeaux.device import Device

from xml.etree import cElementTree as et


class Bridge(Device):
    Lights = {}

#    def __init__(self, address):
#        pass
        #self.bridge_get_lights()

    def __repr__(self):
        self.bridge_get_lights()
#        for light in self.Lights:
#            print 'Light: {name}, State: {state}'.format(name=self.light_name(light), state=self.light_get_state(light).get('state'))
        return '<WeMo Bridge "{name}" Lights: {LightCount} >'.format(name=self.name, LightCount=len(self.Lights))

    def bridge_get_lights(self):
        UDN = self.basicevent.GetMacAddr().get('PluginUDN')
        endDevices = self.bridge.GetEndDevices(DevUDN=UDN,ReqListType='PAIRED_LIST').get('DeviceLists')
        endDevicesList = et.fromstring(endDevices)
        for light in endDevicesList[0][1]:
#            if self.light_name(light) in [ self.light_name(x) for x in self.Lights ]:
            if self.light_name(light) in self.Lights:
                pass
            else:
                #self.Lights.append(light)
                self.Lights[self.light_name(light)] = light
        return self.Lights

    def light_attributes(self, light):
        return {
            'devIndex' : light[0].text,
            'devID' : light[1].text,
            'name' : light[2].text,
            'iconvalue' : light[3].text,
            'firmware' : light[4].text,
            'capabilities' : light[5].text,
            'state' : light[6].text,
            'manufacturer' : light[7].text,
            'model' : light[8].text,
            'certified' : light[9].text
        }

    def light_name(self, light):
        return self.light_attributes(light).get('name')

    def light_get_id(self, light):
        return self.light_attributes(light).get('devID')

    def light_get_state(self, light):
        (
            state, # 0 (off) or 1 (on)
            dim # 0-255 dark to bright
        ) = self.light_attributes(light).get('state').split(':', 1)[0].split(',',1)
        return {
            'state' : state,
            'dim' : dim
        }

    def light_set_state(self, light, state=None, dim=None):
        if state == None:
            state = self.light_get_state(light).get('state')
        if dim == None:
            state = self.light_get_state(light).get('dim')

        sendState = '&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;?&gt;&lt;DeviceStatus&gt;&lt;IsGroupAction&gt;NO&lt;/IsGroupAction&gt;&lt;DeviceID available=&quot;YES&quot;&gt;{devID}&lt;/DeviceID&gt;&lt;CapabilityID&gt;10006,10008&lt;/CapabilityID&gt;&lt;CapabilityValue&gt;{state},{dim}&lt;/CapabilityValue&gt;&lt;/DeviceStatus&gt;'.format(devID=self.light_get_id(light),state=state,dim=dim)

        return self.bridge.SetDeviceStatus(DeviceStatusList=sendState)

