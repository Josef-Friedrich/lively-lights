.. image:: http://img.shields.io/pypi/v/lively_lights.svg
    :target: https://pypi.python.org/pypi/lively_lights

.. image:: https://travis-ci.org/Josef-Friedrich/lively-lights.svg?branch=master
    :target: https://travis-ci.org/Josef-Friedrich/lively-lights


lively-lights
-------------

Lively light scenes on the Philips Hue lamps using Python.

Configuration
^^^^^^^^^^^^^

INI file
""""""""

`~/.lively-lights.ini`

.. code-block:: ini

    [bridge]
    ip = 192.168.3.60
    username = joseffriedrich

    [location]
    latitude = 49.455556
    longitude = 11.078611
    timezone = Europe/Berlin
    elevation = 309


Envrionment variables
"""""""""""""""""""""

.. code-block:: shell

    LIVELY_LIGHTS_BRIDGE_IP=192.168.3.60
    LIVELY_LIGHTS_BRIDGE_USERNAME=joseffriedrich

    LIVELY_LIGHTS_LOCATION_LATITUDE=49.455556
    LIVELY_LIGHTS_LOCATION_LONGITUDE=11.078611
    LIVELY_LIGHTS_LOCATION_TIMEZONE=Europe/Berlin
    LIVELY_LIGHTS_LOCATION_ELEVATION=309
