Tariffs
=======

This library provides a Python toolkit for analysing tariffs for electricity, gas and other utility services.

Use cases include:
- assessing the bill savings associated with energy efficiency, solar or load management
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
At this stage it is best to install the package directly from the repo until a production-ready version is released.

```
pip install git+https://www.github.com/ecologic/tariffs
```

Quickstart
----------
Firstly define your tariff as a JSON data structure e.g. for a very simple block tariff you could apply the tariff below:

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

Next create a CSV file with the time-stamped load data as shown.

```
datetime,electricity_imported
01/01/2018 00:00,0.1
01/01/2018 00:30,0.2
..etc
```

Next import the CSV as as a [Pandas DataFrame](http://pandas.pydata.org/), making sure to parse the datetime field appropriately:

```python
import pandas
import datetime

parser = lambda t: datetime.datetime.strptime(t, '%d/%m/%Y %H:%M')

with open('meter_data.csv') as f:
    meter_data = pandas.read_csv(f, index_col='datetime', parse_dates=True, infer_datetime_format=True,
                                 date_parser=parser)
```

Next construct the Tariff as an [Odin Resource](https://www.github.com/python-odin/odin/) and apply it to the load data as shown.

```python
from odin.codecs import json_codec
from tariffs import Tariff

with open('tariff.json') as f:
    tariff = json_codec.loads(f, Tariff)

bill = tariff.apply(meter_data)
```

To-do
-----
- Re-structure the cost output into a structured Odin Resource
- Add support for Green Button and other serialised consumption data formats
- Add support for ratchet tariffs

This is an early beta and we'll add documentation later but for now you can review the tests for examples of common tariff structures and their application.

Pull requests welcome.