Tariffs
=======

This library provides a Python toolkit for analysing tariffs for electricity, gas and other utility services.

Use cases include:
- assessing the bill savings associated with energy efficiency, solar or active load management
- assessing the benefits of tariff switching

Supported tariff components include:
- flat charges
- block / rate band charges
- seasonal charges
- time-of-use charges
- demand / peak / capacity charges
- scheduled / real-time charges
- feed-in-tariffs / supply payments

Installation
------------
Best to install the package direct from the repo until a production-ready version is released.

```
pip install git+https://www.github.com/ecologic/tariffs
```

Quickstart
----------
Firstly define your tariff as a JSON data structure e.g. for a block tariff you could apply the below:

```javascript
{
    "charges": [
        {
            "rate_bands": [
                {
                    "limit": 100,
                    "rate": 0.1
                },
                {
                    "rate": 0.02
                }
            ]
        }
    ],
    "service": "electricity",
}
```

Next construct the Tariff, using a library called Odin

```python
from odin.codecs import json_codec

with open('tariff.json') as f:
    tariff = json_codec.loads(f, Tariff)
```

Next create a CSV file with the load data

```
datetime,electricity_imported
01/01/2018 00:00,0.1
01/01/2018 00:30,0.2
etc
```

Next import the CSV using as a pandas DataFrame, making sure to include a parser to parse the datetimes appropriately:

```python
parser = lambda t: datetime.datetime.strptime(t, '%d/%m/%Y %H:%M')

with open('meter_data.csv') as f:
    meter_data = pandas.read_csv(f, index_col='datetime', parse_dates=True, infer_datetime_format=True,
                                 date_parser=parser)
```

Next apply the tariff to the meter data

```python
bill = tariff.apply(meter_data)
```

This is an early beta and we'll add documentation later but for now you can review the tests for examples of common tariff structures and their application