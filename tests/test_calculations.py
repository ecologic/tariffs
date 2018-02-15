from tariffs.tariff import Tariff
import pytest
from odin.codecs import dict_codec
import pandas
import datetime


parser = lambda t: datetime.datetime.strptime(t, '%d/%m/%Y %H:%M')


class TestTariff(object):

    @pytest.fixture
    def meter_data(self):
        with open('./fixtures/test_load_data.csv') as f:
            meter_data = pandas.read_csv(f, index_col='datetime', parse_dates=True, infer_datetime_format=True,
                                         date_parser=parser)
        return meter_data

    @pytest.fixture
    def block_tariff(self):
        block_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate_bands": [
                            {
                                "limit": 10,
                                "rate": 0.1
                            },
                            {
                                "rate": 0.01
                            }
                        ]
                    }
                ],
                "service": "electricity",
                "consumption_unit": "kWh",
                "demand_unit": "kVA",
                "billing_period": "monthly"
            }, Tariff
        )
        return block_tariff

    @pytest.fixture
    def seasonal_tariff(self):
        seasonal_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate": 0.1,
                        "season": {
                            "name": "summer",
                            "from_month": 1,
                            "from_day": 1,
                            "to_month": 4,
                            "to_day": 1
                        }
                    },
                    {
                        "rate": 0.1,
                        "season": {
                            "name": "winter",
                            "from_month": 4,
                            "from_day": 1,
                            "to_month": 12,
                            "to_day": 31
                        }
                    }
                ],
                "service": "electricity",
                "consumption_unit": "kWh",
                "demand_unit": "kVA",
                "billing_period": "monthly"
            }, Tariff
        )
        return seasonal_tariff

    @pytest.fixture
    def tou_tariff(self):
        tou_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate": 0.1,
                        "time": {
                            "name": "peak",
                            "periods": [
                                {
                                    "from_hour": 14,
                                    "from_minute": 0,
                                    "to_hour": 19,
                                    "to_minute": 59
                                }
                            ]
                        }
                    },
                    {
                        "rate": 0.1,
                        "time": {
                            "name": "shoulder",
                            "periods": [
                                {
                                    "from_hour": 10,
                                    "from_minute": 0,
                                    "to_hour": 13,
                                    "to_minute": 59
                                },
                                {
                                    "from_hour": 20,
                                    "from_minute": 0,
                                    "to_hour": 21,
                                    "to_minute": 59
                                }
                            ]
                        }
                    },
                    {
                        "rate": 0.1,
                        "time": {
                            "name": "off-peak",
                            "periods": [
                                {
                                    "from_hour": 0,
                                    "from_minute": 0,
                                    "to_hour": 9,
                                    "to_minute": 59
                                },
                                {
                                    "from_hour": 22,
                                    "from_minute": 0,
                                    "to_hour": 23,
                                    "to_minute": 59
                                }
                            ]
                        }
                    }
                ],
                "service": "electricity",
                "consumption_unit": "kWh",
                "demand_unit": "kVA",
                "billing_period": "monthly",
            }, Tariff
        )
        return tou_tariff

    @pytest.fixture
    def scheduled_tariff(self):
        scheduled_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate_schedule": [
                            {
                                "datetime":"2018-01-01T00:00:00Z",
                                "rate": 0.1
                            },
                            {
                                "datetime":"2018-01-01T00:30:00Z",
                                "rate": 0.2
                            },
                            {
                                "datetime": "2018-01-01T01:00:00Z",
                                "rate": 0.3
                            }
                        ]
                    }
                ],
                "service": "electricity",
                "energy_unit": "kWh",
                "demand_unit": "kVA"
            }, Tariff
        )
        return scheduled_tariff

    @pytest.fixture
    def supply_payment_tariff(self):
        supply_payment_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate": -0.1,
                        "meter": "electricity_exported"
                    }
                ],
                "service": "electricity"
            }, Tariff
        )
        return supply_payment_tariff

    @pytest.fixture
    def demand_tariff(self):
        demand_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate": 0.1,
                        "type": "demand"
                    }
                ],
                "service": "electricity",
                "demand_window": "15min",
                "billing_period": "monthly"
            }, Tariff
        )
        return demand_tariff

    def test_block_tariff(self, block_tariff, meter_data):
        expected_bill = 1.0
        actual_bill = block_tariff.apply(meter_data)
        assert actual_bill == expected_bill

    def test_seasonal_tariff(self, seasonal_tariff, meter_data):
        expected_bill = 1.0
        actual_bill = seasonal_tariff.apply(meter_data)
        assert actual_bill == expected_bill

    def test_tou_tariff(self, tou_tariff, meter_data):
        expected_bill = 1.0
        actual_bill = tou_tariff.apply(meter_data)
        assert actual_bill == expected_bill

    def test_scheduled_tariff(self, scheduled_tariff, meter_data):
        expected_bill = 1.0
        actual_bill = scheduled_tariff.apply(meter_data)
        assert actual_bill == expected_bill

    def test_supply_payment(self, supply_payment_tariff, meter_data):
        expected_bill = 1.0
        actual_bill = supply_payment_tariff.apply(meter_data)
        assert actual_bill == expected_bill

    def test_demand_tariff(self, demand_tariff, meter_data):
        expected_bill = 1.0
        actual_bill = demand_tariff.apply(meter_data)
        assert actual_bill == expected_bill
