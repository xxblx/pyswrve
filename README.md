# pyswrve

pyswrve is an unofficial Python wrapper for [Swrve Non-Client APIs](https://docs.swrve.com/swrves-apis/non-client-apis/):
* [Export API](http://docs.swrve.com/developer-documentation/api-guides/non-client-apis/swrve-export-api-guide/) (ready)
* [Items API](https://docs.swrve.com/swrves-apis/non-client-apis/swrve-items-api-guide/) (todo)

# Installation

`pip install pyswrve`

# Usage

```
import pyswrve

swrve = pyswrve.ExportApi(api_key='your_app_key', personal_key='you_personal_key')
```

You can save api_key and personal_key to config file (default: `$HOME/.pyswrve`) with `save_config` method

```
swrve.save_config()
```

Try to get DAU stats
```
from datetime import datetime

start = datetime(2015, 1, 31)
stop = datetime(2015, 2, 1)

swrve.set_dates(start, stop)

swrve.get_kpi('dau', segment='SomeActiveUsers')
[['D-2015-01-31', 19232.00], ['D-2015-02-01', 18762.00]]
```
