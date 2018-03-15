import odin
from odin.codecs import dict_codec
from collections import defaultdict
import datetime
import pandas


SERVICE_CHOICES = (
    ('electricity', 'electricity'),
    ('gas', 'gas'),
    ('water', 'water'),
)

SECTOR_CHOICES = (
    ('residential', 'residential'),
    ('commercial', 'commercial'),
    ('industrial', 'industrial'),
    ('lighting', 'lighting'),
)

TOU_CHOICES = (
    ('peak', 'peak'),
    ('off_peak', 'off peak'),
    ('shoulder', 'shoulder'),
    ('mid_peak', 'mid peak'),
)

SEASON_CHOICES = (
    ('summer', 'summer'),
    ('autumn', 'autumn'),
    ('winter', 'winter'),
    ('spring', 'spring'),
)

CONSUMPTION_UNIT_CHOICES = (
    ('kWh', 'kilowatt-hours'),
    ('MJ', 'megajoules'),
    ('btu', 'british thermal units'),
    ('kL', 'kilolitres'),
    ('gal', 'gallons'),
    ('kWh/kW', 'kWh/kW'), # TODO this doesn't appear to be a meaningful value but used throughout database, investigate
    ('kWh/hp', 'kWh/hp'), # TODO this doesn't appear to be a meaningful value but used throughout database, investigate
)

DEMAND_UNIT_CHOICES = (
    ('kW', 'kilowatts'),
    ('hp', 'hp'),
    ('kVA', 'kVA'),
)

CHARGE_TYPE_CHOICES = (
    ('fixed', 'Fixed'),
    ('minimum', 'Minimum'),
    ('consumption', 'Consumption'),
    ('demand', 'Demand'),
    ('generation', 'Generation'),
)

PERIOD_CHOICES = (
    ('daily', 'Daily'),
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('annually', 'Annually'),
)

DEMAND_WINDOW_CHOICES = (
    ('15min', '15min'),
    ('30min', '30min'),
    ('hourly', 'hourly')
)

PERIOD_TO_TIMESTEP = {
    '15min': '15min',
    '30min': '30min',
    'hourly': 'H',
    'daily': 'DS',
    'weekly': 'WS',
    'monthly': 'MS',
    'quarterly': 'QS',
    'annually': 'A',
}


class CostItem(odin.Resource):
    name = odin.StringField(null=True)
    code = odin.StringField(null=True)
    type = odin.StringField(null=True)
    season = odin.StringField(null=True)
    time = odin.StringField(null=True)
    cost = odin.FloatField()


class Cost(odin.Resource):
    name = odin.StringField(null=True)
    code = odin.StringField(null=True)
    items = odin.ArrayOf(CostItem)

    @odin.calculated_field
    def cost(self):
        cost = 0.0
        for cost_item in self.items:
            cost += cost_item.cost
        return cost


class RateBand(odin.Resource):
    """A specific band within a block pricing rate structure"""
    limit = odin.FloatField(null=True, default=999999999.9, use_default_if_not_provided=True)
    rate = odin.FloatField()


class Period(odin.Resource):
    """A period within a time-of-use pricing rate structure"""
    from_weekday = odin.IntegerField(min_value=0, null=True, use_default_if_not_provided=True, default=0)
    to_weekday = odin.IntegerField(max_value=6, null=True, use_default_if_not_provided=True, default=6)
    from_hour = odin.IntegerField(min_value=0, max_value=23, null=True, use_default_if_not_provided=True, default=0)
    from_minute = odin.IntegerField(min_value=0, max_value=59, null=True, use_default_if_not_provided=True, default=0)
    to_hour = odin.IntegerField(min_value=0, max_value=23, null=True, use_default_if_not_provided=True, default=23)
    to_minute = odin.IntegerField(min_value=0, max_value=59, null=True, use_default_if_not_provided=True, default=59)


class Time(odin.Resource):
    """A time within a time-of-use pricing rate structure"""
    name = odin.StringField()
    periods = odin.ArrayOf(Period)


class ScheduleItem(odin.Resource):
    """An item in a scheduled or real-time pricing rate structure"""
    datetime = odin.NaiveDateTimeField(ignore_timezone=True)
    rate = odin.FloatField()


class Season(odin.Resource):
    """A season within a seasonal pricing rate structure"""
    name = odin.StringField()
    from_month = odin.IntegerField(min_value=1, max_value=12, null=True, use_default_if_not_provided=True, default=1)
    from_day = odin.IntegerField(min_value=1, max_value=31, null=True, use_default_if_not_provided=True, default=12)
    to_month = odin.IntegerField(min_value=1, max_value=12, null=True, use_default_if_not_provided=True, default=12)
    to_day = odin.IntegerField(min_value=1, max_value=31, null=True, use_default_if_not_provided=True, default=31)


class Charge(odin.Resource):
    """A charge component of a tariff structure"""
    rate = odin.FloatField(null=True)
    rate_bands = odin.ArrayOf(RateBand, null=True)
    rate_schedule = odin.ArrayOf(ScheduleItem, null=True)
    time = odin.ObjectAs(Time, null=True)
    season = odin.ObjectAs(Season, null=True)
    type = odin.StringField(choices=CHARGE_TYPE_CHOICES, null=True, default='consumption',
                            use_default_if_not_provided=True)

    @odin.calculated_field
    def name(self):
        season = self.season.name if self.season else None
        time = self.time.name if self.time else None
        scheduled = 'scheduled' if self.rate_schedule else None
        return str(self.type or '') + str(season or '') + str(time or '') + str(scheduled or '')

class Times(odin.Resource):
    """"""
    off_peak_end = odin.NaiveTimeField(null=True)
    early_shoulder_end = odin.NaiveTimeField(null=True)
    early_peak_end = odin.NaiveTimeField(null=True)
    mid_peak_end = odin.NaiveTimeField(null=True)
    peak_end = odin.NaiveTimeField(null=True)
    late_shoulder_end = odin.NaiveTimeField(null=True)


class Seasons(odin.Resource):
    """"""
    summer_end = odin.DateField(null=True)
    autumn_end = odin.DateField(null=True)
    winter_end = odin.DateField(null=True)
    spring_end = odin.DateField(null=True)


class Tariff(odin.Resource):
    """A collection of charges associated with a specific utility service"""
    name = odin.StringField(null=True)
    code = odin.StringField(null=True)
    utility_name = odin.StringField(null=True)
    utility_code = odin.StringField(null=True)
    service = odin.StringField(choices=SERVICE_CHOICES, null=True)
    sector = odin.StringField(choices=SECTOR_CHOICES, null=True)
    description = odin.StringField(null=True)
    currency = odin.StringField(null=True)
    timezone = odin.StringField(null=True)
    min_consumption = odin.FloatField(null=True)
    max_consumption = odin.FloatField(null=True)
    min_demand = odin.FloatField(null=True)
    max_demand = odin.FloatField(null=True)
    charges = odin.ArrayOf(Charge, null=True)
    monthly_charge = odin.FloatField(null=True)
    minimum_charge = odin.FloatField(null=True)
    times = odin.DictAs(Times, null=True)
    seasons = odin.DictAs(Seasons, null=True)
    net_metering = odin.BooleanField(null=True)
    billing_period = odin.StringField(choices=PERIOD_CHOICES, null=True, default='monthly', use_default_if_not_provided=True)
    demand_window = odin.StringField(choices=DEMAND_WINDOW_CHOICES, null=True, default='30min', use_default_if_not_provided=True)
    consumption_unit = odin.StringField(choices=CONSUMPTION_UNIT_CHOICES, null=True)
    demand_unit = odin.StringField(choices=DEMAND_UNIT_CHOICES, null=True)

    @odin.calculated_field
    def charge_types(self):
        charge_types = set()
        for charge in self.charges:
            if charge.season:
                charge_types.add('seasonal')
            if charge.time:
                charge_types.add('tou')
            if charge.rate_bands:
                charge_types.add('block')
            if charge.rate_schedule:
                charge_types.add('scheduled')
            if charge.type == 'demand':
                charge_types.add('demand')
            if charge.type == 'consumption':
                charge_types.add('consumption')
            if charge.type == 'generation':
                charge_types.add('generation')

        return list(charge_types)

    def calc_charge(self, name, row, charge, cost_items, block_accum_dict):
        if charge.rate:
            cost_items[name]['cost'] += charge.rate * float(row[charge.type])
        if charge.rate_bands:
            charge_time_step = float()
            for rate_band_index, rate_band in enumerate(charge.rate_bands):
                if block_accum_dict[name] > rate_band.limit:
                    continue
                block_usage = max((min(
                    (rate_band.limit - block_accum_dict[name], row[charge.type] - block_accum_dict[name])), 0.0))
                charge_time_step += rate_band.rate * block_usage
                block_accum_dict[name] += block_usage
            cost_items[name]['cost'] += charge_time_step

        return cost_items, block_accum_dict

    def apply_by_charge_type(self, meter_data, cost_items, charge_type='consumption'):
        """
            Calculates the cost of energy given a tariff and load.

            :param meter_data: a three-column pandas array with datetime, imported energy (kwh), exported energy (kwh)
            :return: a dictionary containing the charge components (e.g. off_peak, shoulder, peak, total)
        """

        block_accum_dict = defaultdict(float)

        for dt, row in meter_data.iterrows():
            time = datetime.time(hour=dt.hour, minute=dt.minute)

            # If the billing cycle changes over, reset block charge accumulations
            if (charge_type == 'consumption' and
                self.billing_period == 'monthly' and dt.day == 1 and dt.hour == 0 and dt.minute == 0 or
                self.billing_period == 'quarterly' and dt.month % 3 and dt.day == 1 and dt.hour == 0 and dt.minute == 0 or
                self.billing_period == 'annually' and dt.month == 1 and dt.day == 1 and dt.hour == 0 and dt.minute == 0):
                block_accum_dict = defaultdict(float)
            if charge_type == 'demand':
                block_accum_dict = defaultdict(float)

            if self.charges:
                for charge in self.charges:
                    if charge.type == charge_type or (charge_type == 'consumption' and charge.type == 'generation'):
                        if charge.time and charge.season:
                            if datetime.date(year=dt.year, month=charge.season.from_month, day=charge.season.from_day) \
                                    <= dt.date() <= datetime.date(year=dt.year, month=charge.season.to_month,
                                                                 day=charge.season.to_day):
                                for period in charge.time.periods:
                                    if period.from_weekday <= dt.dayofweek <= period.to_weekday and datetime.time(
                                            hour=period.from_hour, minute=period.from_minute) <= time <= datetime.time(
                                            hour=period.to_hour, minute=period.to_minute):
                                        cost_items, block_accum_dict = self.calc_charge(
                                            charge.name, row, charge, cost_items, block_accum_dict)
                                        break
                        elif charge.season:
                            if datetime.date(year=dt.year, month=charge.season.from_month, day=charge.season.from_day)\
                                    <= dt.date() <= datetime.date(year=dt.year, month=charge.season.to_month,
                                                                 day=charge.season.to_day):
                                cost_items, block_accum_dict = self.calc_charge(
                                    charge.name, row, charge, cost_items, block_accum_dict)
                        elif charge.time:
                            for period in charge.time.periods:
                                if period.from_weekday <= dt.dayofweek <= period.to_weekday and datetime.time(
                                        hour=period.from_hour, minute=period.from_minute) <= time <= datetime.time(
                                        hour=period.to_hour, minute=period.to_minute):
                                    cost_items, block_accum_dict = self.calc_charge(
                                        charge.name, row, charge, cost_items, block_accum_dict)
                        elif charge.rate_schedule:
                            for schedule_item in charge.rate_schedule:
                                if dt.to_pydatetime() < schedule_item.datetime:
                                    cost_items[charge.type + 'scheduled']['cost'] += schedule_item.rate * float(row[charge.type])
                                    break
                        else:
                            cost_items, block_accum_dict = self.calc_charge(
                                charge.type, row, charge, cost_items, block_accum_dict)

        return cost_items

    def apply(self, meter_data, start=None, end=None):
        """
            Calculates the cost of energy given a tariff and load.

            :param meter_data: a three-column pandas array with datetime, imported energy (kwh), exported energy (kwh)
            :param start: an optional datetime to select the commencement of the bill calculation
            :param end: an optional datetime to select the termination of the bill calculation
            :return: a dictionary containing the charge components (e.g. off_peak, shoulder, peak, total)
        """
        meter_data.truncate(before=start, after=end)

        # Create empty dict to hold calculated cost items
        cost_items = dict()
        for charge in self.charges:
            season = charge.season.name if charge.season else None
            time = charge.time.name if charge.time else None
            cost_items[charge.name] = {
                'name': charge.name,
                'type': charge.type,
                'season': season,
                'time': time,
                'cost': 0.0,
            }

        if 'consumption' in self.charge_types or 'generation' in self.charge_types:
            consumption_data = meter_data
            # Resample meter data if finer resolution data not required by the specified tariff types
            if 'tou' not in self.charge_types:
                if 'seasonal' in self.charge_types:
                    consumption_data = meter_data.resample('D').sum()
                else:
                    consumption_data = meter_data.resample(PERIOD_TO_TIMESTEP[self.billing_period]).sum()

            cost_items.update(self.apply_by_charge_type(consumption_data, cost_items, 'consumption'))

        if 'demand' in self.charge_types:
            # Resample meter data to the demand window and then take the maximum for each billing period
            demand_data = meter_data.resample(PERIOD_TO_TIMESTEP[self.demand_window]).mean()
            peak_monthly = demand_data.resample(PERIOD_TO_TIMESTEP[self.billing_period]).max()
            cost_items.update(self.apply_by_charge_type(peak_monthly, cost_items, 'demand'))

        # Transform the output data into the specified output format
        cost_dict = {
            'name': self.name,
            'code': self.code,
            'items': cost_items.values()
        }

        return dict_codec.load(cost_dict, Cost)


class Spec(odin.Resource):

    tariffs = odin.ArrayOf(Tariff)
