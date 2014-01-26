from .switch import Switch

class Insight(Switch):

    def __repr__(self):
        return '<WeMo Insight "{name}">'.format(name=self.name)

    @property
    def today_kwh(self):
        return self.insight.GetTodayKWH()

    @property
    def current_power(self):
        """
        Returns the current power usage in mW.
        """
        return self.insight.GetPower()

    @property
    def today_on_time(self):
        return self.insight.GetTodayONTime()

    @property
    def on_for(self):
        return self.insight.GetONFor()

    @property
    def in_standby_since(self):
        return self.insight.GetInSBYSince()

    @property
    def today_standby_time(self):
        return self.insight.GetTodaySBYTime()

