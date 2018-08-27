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


Coding example
""""""""""""""

.. code-block:: python

    #! /usr/bin/env python3

    from lively_lights.environment import ReachableLightsFactory, ReachableLights, DayNight
    from lively_lights.scenes import Launcher
    import lively_lights
    import os
    import threading
    import time


    def get_path(filename):
        return os.path.join(os.path.dirname(__file__), filename)


    def launch(reachable_lights, scene_configs_file):
        launcher = Launcher(
            hue.bridge,
            reachable_lights,
            scene_configs_file=get_path(scene_configs_file),
            verbosity_level=hue.bridge.verbosity_level,
        )
        launcher.launch(endless=True)


    hue = lively_lights.Hue(verbosity_level=2)

    day_night = DayNight(
        hue.config.get('location', 'latitude'),
        hue.config.get('location', 'longitude'),
        hue.config.get('location', 'timezone'),
        hue.config.get('location', 'elevation'),
    )

    factory = ReachableLightsFactory(hue.bridge, day_night, refresh_interval=30)
    lights_bedroom = factory.get_lights(4, 5, 6)
    lights_livingroom = factory.get_lights(1, 2, 3, 7, 8, 9)
    lights_livingroom_cupboard = ReachableLights(
        hue.bridge,
        day_night,
        light_ids=(7, 8, 9),
        not_during_daytime=True,
        not_host_up='192.168.3.21:22',
        refresh_interval=30,
    )
    lights_livingroom_ceiling = factory.get_lights(1, 2, 3)
    lights_office = factory.get_lights(10, 11)

    for args in ((lights_bedroom, 'bedroom.yml'),
                 (lights_livingroom_cupboard, 'livingroom.yml'),
                 (lights_livingroom_ceiling, 'livingroom.yml'),
                 (lights_office, 'office.yml'),):
        thread = threading.Thread(target=launch, args=args)
        thread.start()
