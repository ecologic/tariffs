from tariffs.tariff import Tariff
import pytest
from odin.codecs import json_codec
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
    def tariff_file(self):
        with open('./fixtures/tariff_multi_BTOWN.json') as f:
            tariff = json_codec.load(f, Tariff)
        return tariff

    @pytest.fixture
    def fixed_tariff(self):
        with open('./fixtures/fixed_tariff.json') as f:
            tariff = json_codec.load(f, Tariff)
        return tariff

    @pytest.fixture
    def block_tariff(self):
        with open('./fixtures/block_tariff.json') as f:
            tariff = json_codec.load(f, Tariff)
        return tariff

    @pytest.fixture
    def seasonal_tariff(self):
        with open('./fixtures/seasonal_tariff.json') as f:
            tariff = json_codec.load(f, Tariff)
        return tariff

    @pytest.fixture
    def tou_tariff(self):
        with open('./fixtures/tou_tariff.json') as f:
            tariff = json_codec.load(f, Tariff)
        return tariff

    @pytest.fixture
    def scheduled_tariff(self):
        with open('./fixtures/scheduled_tariff.json') as f:
            tariff = json_codec.load(f, Tariff)
        return tariff

    @pytest.fixture
    def supply_payment_tariff(self):
        with open('./fixtures/supply_payment.json') as f:
            tariff = json_codec.load(f, Tariff)
        return tariff

    @pytest.fixture
    def demand_tariff(self):
        with open('./fixtures/demand_tariff.json') as f:
            tariff = json_codec.load(f, Tariff)
        return tariff

    def test_fixed_tariff(self, fixed_tariff, meter_data):
        expected_bill = 12.0
        actual_bill = fixed_tariff.apply(meter_data)
        assert actual_bill.cost == expected_bill

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