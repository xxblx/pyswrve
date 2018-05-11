# pyswrve

pyswrve is an unofficial Python wrapper for [Swrve Export API](http://docs.swrve.com/developer-documentation/api-guides/non-client-apis/swrve-export-api-guide/)

# Installation

`python setup.py install`

# Usage

```
import pyswrve
s = pyswrve.API(api_key='some_key', personal_key='some_key2')
s.set_dates(period='week', period_count=2)  # last 2 weeks
```

You can save api_key and personal_key to config file ($HOME/.pyswrve) with save_defaults method

```
import pyswrve
s = pyswrve.API(api_key='some_key', personal_key='some_key2')
s.save_config()
```

```
import pyswrve
s = pyswrve.API()
s.set_dates(start='2015-01-31', stop='2015-03-15')
s.get_evt_stat(ename='some.event.name', payload='level', payload_val='25')
{'25': [['D-2015-01-31', 126.00], ['D-2015-02-01', 176.00]]}
```

[Check wiki for details](https://github.com/xxblx/pyswrve/wiki).
