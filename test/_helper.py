import os
from unittest import mock
import lively_lights

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

    reachable_lights.list = mock.Mock(return_value=return_list)

    return reachable_lights
