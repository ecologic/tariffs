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
                                "rate": 1.0
                            },
                            {
                                "rate": 1.0
                            }
                        ]
                    }
                ]
            }, Tariff
        )
        return block_tariff

    @pytest.fixture
    def seasonal_tariff(self):
        seasonal_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate": 1.0,
                        "season": {
                            "name": "summer",
                            "from_month": 1,
                            "from_day": 1,
                            "to_month": 3,
                            "to_day": 31
                        }
                    },
                    {
                        "rate": 1.0,
                        "season": {
                            "name": "winter",
                            "from_month": 4,
                            "from_day": 1,
                            "to_month": 12,
                            "to_day": 31
                        }
                    }
                ]
            }, Tariff
        )
        return seasonal_tariff

    @pytest.fixture
    def tou_tariff(self):
        tou_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate": 1.0,
                        "time": {
                            "name": "peak",
                            "periods": [
                                {
                                    "from_weekday": 0,
                                    "to_weekday": 4,
                                    "from_hour": 14,
                                    "to_hour": 19,
                                }
                            ]
                        }
                    },
                    {
                        "rate": 1.0,
                        "time": {
                            "name": "shoulder",
                            "periods": [
                                {
                                    "from_weekday": 0,
                                    "to_weekday": 4,
                                    "from_hour": 10,
                                    "to_hour": 13,
                                },
                                {
                                    "from_weekday": 0,
                                    "to_weekday": 4,
                                    "from_hour": 20,
                                    "to_hour": 21,
                                }
                            ]
                        }
                    },
                    {
                        "rate": 1.0,
                        "time": {
                            "name": "off-peak",
                            "periods": [
                                {
                                    "from_weekday": 0,
                                    "to_weekday": 4,
                                    "from_hour": 0,
                                    "from_minute": 0,
                                    "to_hour": 9,
                                    "to_minute": 59
                                },
                                {
                                    "from_weekday": 0,
                                    "to_weekday": 4,
                                    "from_hour": 22,
                                    "from_minute": 0,
                                    "to_hour": 23,
                                    "to_minute": 59
                                },
                                {
                                    "from_weekday": 5,
                                    "to_weekday": 6
                                }
                            ]
                        }
                    }
                ]
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
                                "rate": 1.0
                            },
                            {
                                "datetime":"2018-06-01T00:30:00Z",
                                "rate": 1.0
                            },
                            {
                                "datetime": "2018-12-31T01:00:00Z",
                                "rate": 1.0
                            }
                        ]
                    }
                ]
            }, Tariff
        )
        return scheduled_tariff

    @pytest.fixture
    def supply_payment_tariff(self):
        supply_payment_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate": -1.0,
                        "type": "generation"
                    }
                ]
            }, Tariff
        )
        return supply_payment_tariff

    @pytest.fixture
    def demand_tariff(self):
        demand_tariff = dict_codec.load(
            {
                "charges": [
                    {
                        "rate": 1.0,
                        "type": "demand"
                    }
                ]
            }, Tariff
        )
        return demand_tariff

    def test_block_tariff(self, block_tariff, meter_data):
        expected_bill = 35040.0
        actual_bill = block_tariff.apply(meter_data)
        assert actual_bill.cost == expected_bill

    def test_seasonal_tariff(self, seasonal_tariff, meter_data):
        expected_bill = 35040.0
        actual_bill = seasonal_tariff.apply(meter_data)
        assert actual_bill.cost == expected_bill

    def test_tou_tariff(self, tou_tariff, meter_data):
        expected_bill = 35040.0
        actual_bill = tou_tariff.apply(meter_data)
        assert actual_bill.cost == expected_bill

    def test_scheduled_tariff(self, scheduled_tariff, meter_data):
        expected_bill = 35040.0
        actual_bill = scheduled_tariff.apply(meter_data)
        assert actual_bill.cost == expected_bill

    def test_supply_payment(self, supply_payment_tariff, meter_data):
        expected_bill = -35040.0
        actual_bill = supply_payment_tariff.apply(meter_data)
        assert actual_bill.cost == expected_bill

    def test_demand_tariff(self, demand_tariff, meter_data):
        expected_bill = 12.0
        actual_bill = demand_tariff.apply(meter_data)
        assert actual_bill.cost == expected_bill
