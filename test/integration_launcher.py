#! /usr/bin/env python3
""" Test manually the interface of the package."""

from lively_lights.scenes import Launcher
from lively_lights import Hue

_rainbow = {
    'title': 'Rainbow',
    'description': 'Cycle between three colors',
    'scene_name': 'sequence',
    'duration': 3,
    'properties': {
        'brightness': 254,
        'hue_sequence': [0, 40000, 30000],
        'sleep_time': 2,
        'transition_time': 1,
    },
}

_breath = {
    'title': 'Breath',
    'description': 'Breathing colors',
    'scene_name': 'breath',
    'duration': 3,
    'properties': {
        'time_range': (1, 2),
    },
}

_invalid_breath = {
    'title': 'Invalid breath',
    'description': 'scene has not property time',
    'scene_name': 'breath',
    'duration': 3,
    'properties': {
        'xxx': 1,
    },
}

hue = Hue()
lauchner = Launcher(hue.bridge, hue.reachable_lights, [_rainbow, _invalid_breath])
