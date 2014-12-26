from datetime import datetime
from .switch import Switch

class Insight(Switch):

    def __repr__(self):
        return '<WeMo Insight "{name}">'.format(name=self.name)

    @property
    def insight_params(self):
        params = self.insight.GetInsightParams().get('InsightParams')
        (
            state,  # 0 if off, 1 if on, 8 if on but load is off
            lastchange,
            onfor,  # seconds
            ontoday,  # seconds
            ontotal,  # seconds
            timeperiod,  # The period over which averages are calculated
            _x,  # This one is always 19 for me; what is it?
            currentmw,
            todaymw,
            totalmw,
            powerthreshold
        ) = params.split('|')
        return {'state': state,
                'lastchange': datetime.fromtimestamp(int(lastchange)),
                'onfor': int(onfor),
                'ontoday': int(ontoday),
                'ontotal': int(ontotal),
                'todaymw': int(float(todaymw)),
                'totalmw': int(float(totalmw)),
                'currentpower': int(float(currentmw))}

    @property
    def today_kwh(self):
        return self.insight_params['todaymw'] * 1.6666667e-8

    @property
    def current_power(self):
        """
        Returns the current power usage in mW.
        """
        return self.insight_params['currentpower']

    @property
    def today_on_time(self):
        return self.insight_params['ontoday']

    @property
    def on_for(self):
        return self.insight_params['onfor']

    @property
    def last_change(self):
        return self.insight_params['lastchange']

    @property
    def today_standby_time(self):
        return self.insight_params['ontoday']

    @property
    def ontotal(self):
        return self.insight_params['ontotal']

    @property
    def totalmw(self):
        return self.insight_params['totalmw']
