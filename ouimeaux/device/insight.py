from .switch import Switch

class Insight(Switch):

    def __repr__(self):
        return '<WeMo Insight "{name}">'.format(name=self.name)

    @property
    def insight_params(self):
        params = self.insight.GetInsightParams().get('InsightParams')
['1',
 '1401624771',
 '493',
 '513',
 '161285',
 '1209600',

 '20',
 '19580',
 '159187',
 '49942514.000000',
 '8000']
        (
            state,
            lastchange,
            onfor,
            ontoday,
            ontotal,
            timeperiod,
            x,
            currentmw,
            z,
            j,
            powerthreshold


        )
        state, lastchange, onfor, ontoday, ontotal, twoweeks, todaymw, totalmw, u3 = params.split('|')
        return {
                'state': state,
                'lastchange': datetime.fromtimestamp(int(lastchange)),
                'onfor': int(laston),
                'ontoday': int(ontoday),
                'ontotal': int(total),
                'todaymw': todaymw,
                'totalmw': totalmw,
                'currentpower': u2
                }

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

