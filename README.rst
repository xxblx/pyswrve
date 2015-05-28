
pyswrve
=======

**pyswrve** is an unofficial Python wrapper for `Swrve <https://www.swrve.com/>`_ 
`Export API <http://docs.swrve.com/developer-documentation/api-guides/non-client-apis/38838468/>`_

Quickstart
==========

Install
-------

.. code:: python

    python setup.py install 
    
Usage
-----

.. code:: python

    import pyswrve
    s = pyswrve.API(api_key='some_key', personal_key='some_key2')
    s.set_dates(period='week', period_count=2)  # last 2 weeks
    print s.get_kpi('dau')
    # will print list where elements are lists like ['date', 'value']
    # etc... 
    
You can save api_key and personal_key to config file ($HOME/.pyswrve) with 
save_defaults method
   
.. code:: python
    
    import pyswrve
    s = pyswrve.API(api_key='some_key', personal_key='some_key2')
    s.save_defaults()
    
After this you don't need to set api key and personal key on object creation. 

.. code:: python

    import pyswrve
    s = pyswrve.API()
    s.set_dates(start='2015-01-31', stop='2015-03-15')
    print s.get_evt_stat(ename='some.event.name', payload='player_level', payload_val='25')
    # will print triggering count for event "some.event.name" with 
    # payload "player_level" for 25 level since Jan 31 2015 up to Mar 15 2015
    # as dict where key is payload value (25) and value is list with list-elements
    # like {'25': [['D-2015-01-31', 126.00], ['D-2015-02-01', 176.00], ... ]}

`Check wiki for details <https://github.com/xxblx/pyswrve/wiki>`_. 


Additional info
===============

If you have any questions feel free to contact with me: olkozlov@playrix.com. 

Oleg Kozlov (xxblx), 2015
