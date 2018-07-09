import os
from unittest import mock
import lively_lights
from lively_lights.environment import DayNight

command_name = 'lively-lights.py'

config_file = os.path.join(os.path.dirname(__file__), 'lively-lights.ini')


class MockLight(object):

    def __init__(self, light_id):
        self.light_id = light_id


def mock_light_list(light_ids):
    lights = []
    for light_id in light_ids:
        lights.append(MockLight(light_id))
    return lights


def get_reachable_lights(light_ids, reachable_light_ids=None):
    reachable_lights = lively_lights.ReachableLights(mock.Mock(), light_ids)

    if reachable_light_ids:
        return_list = mock_light_list(reachable_light_ids)
    else:
        return_list = mock_light_list(light_ids)

    reachable_lights._get_reachable = mock.Mock(return_value=return_list)
    reachable_lights.is_reachable = mock.Mock(return_value=True)

    return reachable_lights


def get_day_night():
    return DayNight(49.455556, 11.078611, 'Europe/Berlin', 309)


def mock_light(light_id, reachable=True):
    light = mock.MagicMock()
    light.light_id = light_id
    light.reachable = reachable
    return light


def mock_get_item(self, key):
    for light in self.lights:
        if light.light_id == key:
            return light


def mock_bridge(light_configs):
    lights = []
    for light_config in light_configs:
        lights.append(mock_light(light_config[0], light_config[1]))
    bridge = mock.MagicMock()
    bridge.lights = lights
    bridge.__getitem__ = mock_get_item
    return bridge
