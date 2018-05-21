
"""A collection of scenes."""

from lively_lights import _random as random
from lively_lights._utils import set_light_multiple
from lively_lights import types
from random import randint
import threading
import time
import sys


class Launcher(object):

    """
    Launch scenes.



    :param reachable_lights: An object containing the specified and
      reachable lights.
    :type reachable_lights: lively_lights.ReachableLights

    :param list scene_config_list: A list of `scene_config` dictionaries.


    .. code-block:: python

        scene_config_list = [
            {
                'title': 'Rainbow',
                'description': 'Cycle between three colors',
                'scene_name': 'sequence',
                'duration': 12,
                'properties': {
                    'brightness': 255,
                    'hue_sequence': [0, 40000, 30000],
                    'sleep_time': 2,
                    'transition_time': 1,
                },
            },
            {
                'title': 'Storm',
                'description': 'Stormy weather',
                'scene_name': 'sequence',
                'duration': 13,
                'properties': {
                    'brightness': 10,
                    'hue_sequence': [0, 40000, 30000],
                    'sleep_time': 1,
                    'transition_time': 1,
                },
            },
        ]

    """

    def __init__(self, bridge, reachable_lights, scene_config_list=None):
        self.bridge = bridge
        self.reachable_lights = reachable_lights
        self.scene_config_list = scene_config_list

    @staticmethod
    def _get_scene_class(scene_name):
        class_name = 'Scene{}'.format(scene_name.title())
        return getattr(sys.modules[__name__], class_name)

    def launch_scene(self, scene_config):
        """
        Launch one scene.

        :param dict scene_config: A dictionary holding the configuration of
          the desired scene.

        .. code-block:: python

            scene_config = {
                'title': 'Rainbow',
                'description': 'Cycle between three colors',
                'scene_name': 'sequence',
                'duration': 13,
                'properties': {
                    'brightness': 255,
                    'hue_sequence': [0, 40000, 30000],
                    'sleep_time': 2,
                    'transition_time': 1,
                },
            }

        """
        Scene = self._get_scene_class(scene_config['scene_name'])
        scene = Scene(self.bridge, self.reachable_lights)
        scene.get_properties_from_dict(scene_config['properties'])
        scene.start(scene_config['duration'])


class Scene(object):

    """
    :param reachable_lights: An object containing the specified and
      reachable lights.
    :type reachable_lights: lively_lights.ReachableLights
    """

    properties = {}

    def __init__(self, bridge, reachable_lights, **kwargs):
        self.bridge = bridge
        self.reachable_lights = reachable_lights

        for key, value in kwargs.items():
            if key in self.properties:
                setattr(self, key, value)
            else:
                raise ValueError('Property “{}” is not allowed.'.format(key))

    def get_properties_from_args(self, args):
        for property, value in self.properties.items():
            if hasattr(args, property):
                setattr(self, property, getattr(args, property))

    def get_properties_from_dict(self, dictionary):
        for property, value in self.properties.items():
            if property in dictionary:
                setattr(self, property, dictionary[property])

    def has_property(self, property):
        if not hasattr(self, property) or not getattr(self, property):
            return False
        else:
            return True

    def _set_defaults(self):
        """Should be overwritten."""
        pass

    def _validate(self):
        for property, config in self.properties.items():
            setattr(self, property, config['type'](getattr(self, property)))

    def _run(self, time_out=None):
        """Should be overwritten."""
        pass

    def start(self, time_out=None):
        self._set_defaults()
        self._validate()
        self._run(time_out)


class SceneBreath(Scene):

    properties = {
        'brightness_range': {
            'type': types.brightness_range,
        },
        'hue_range': {
            'type': types.hue_range,
        },
        'time_range': {
            'type': types.time_range,
        },
    }

    def _set_defaults(self):
        self._threads = {}
        self._time_to_end = None

        if not self.has_property('brightness_range'):
            self.brightness_range = (
                random.brightness(max=100),
                random.brightness(min=100),
            )

        if not self.has_property('hue_range'):
            self.hue_range = (random.hue(max=32766), random.hue(min=32767))

        if not self.has_property('time_range'):
            self.time_range = (
                random.time(min=1, max=4, decimal_places=1),
                random.time(min=4, max=8, decimal_places=1),
            )

    def _set_light(self, light_id):
        while True:
            if self.reachable_lights.is_reachable(light_id):
                time_span = random.time(
                    self.time_range[0],
                    self.time_range[1],
                    decimal_places=1
                )

                if self._time_to_end and \
                   time.time() - time_span > self._time_to_end:
                    break
                data = {
                    'hue': randint(*self.hue_range),
                    'transitiontime': types.transition_time(time_span),
                    'bri': randint(*self.brightness_range),
                    'sat': 254,
                }
                set_light_multiple(self.bridge, light_id, data)
                time.sleep(time_span + 0.2)
            else:
                break

    def _run(self, time_out=None):
        if time_out:
            self._time_to_end = time.time() + time_out
        while True:
            if self._time_to_end and self._time_to_end <= time.time():
                break

            for light in self.reachable_lights.list():
                if light.light_id not in self._threads or \
                   not self._threads[light.light_id].is_alive():
                    t = threading.Thread(
                        target=self._set_light,
                        args=(
                            light.light_id,
                        ),
                    )
                    t.start()
                    self._threads[light.light_id] = t

            time.sleep(self.reachable_lights.refresh_interval)


class ScenePendulum(Scene):

    properties = {
        'color1': {
            'type': types.hue,
        },
        'color2': {
            'type': types.hue,
        },
        'lights1': {
            'type': types.light_id_list,
        },
        'lights2': {
            'type': types.light_id_list,
        },
        'sleep_time': {
            'type': types.time,
        },
        'transition_time': {
            'type': types.time,
        },
    }

    def _set_defaults(self):
        if not self.has_property('color1'):
            self.color1 = random.hue()

        if not self.has_property('color2'):
            self.color2 = random.hue()

        if not self.has_property('lights1') or \
           not self.has_property('lights2'):
            self.lights1, self.lights2 = self._distribute_lights()

        if not self.has_property('sleep_time'):
            self.sleep_time = random.time(4, 8)

        if not self.has_property('transition_time'):
            self.transition_time = random.time(1, 3, decimal_places=1)

    def _distribute_lights(self):
        light_ids = self.reachable_lights.list_light_ids()
        random.shuffle(light_ids)
        count = len(light_ids)
        half = int(count / 2)
        return (light_ids[0:half], light_ids[half:])

    def _set_light_group(self, light_ids, hue):
        for light_id in light_ids:
            data = {
                'hue': hue,
                'bri': 254,
                'transitiontime': types.transition_time(self.transition_time),
                'sat': 254,
            }
            set_light_multiple(self.bridge, light_id, data)

    def _run(self, time_out=None):
        begin = time.time()
        while True:
            if time_out and \
               time.time() - begin + self.sleep_time * 2 >= time_out:
                break
            self._set_light_group(self.lights1, self.color1)
            self._set_light_group(self.lights2, self.color2)
            time.sleep(self.sleep_time)
            self._set_light_group(self.lights1, self.color2)
            self._set_light_group(self.lights2, self.color1)
            time.sleep(self.sleep_time)

        if time_out:
            time_left = time.time() - begin - time_out
            if time_left > 0:
                time.sleep(time_left)


class SceneSequence(Scene):

    properties = {
        'brightness': {
            'type': types.brightness,
        },
        'hue_sequence': {
            'type': types.hue_list,
        },
        'sleep_time': {
            'type': types.time,
        },
        'transition_time': {
            'type': types.time,
        },
    }

    def _set_defaults(self):
        if not self.has_property('brightness'):
            self.brightness = random.brightness(min=100)

        if not self.has_property('hue_sequence'):
            self.hue_sequence = (
                random.hue(),
                random.hue(),
                random.hue(),
                random.hue(),
            )

        if not self.has_property('sleep_time'):
            self.sleep_time = random.time(4, 8)

        if not self.has_property('transition_time'):
            self.transition_time = random.time(1, 3, decimal_places=1)

    def _run(self, time_out=None):
        begin = time.time()
        try:
            while True:
                for hue in self.hue_sequence:
                    for light in self.reachable_lights.list():
                        data = {
                            'hue': hue,
                            'bri': self.brightness,
                            'transitiontime': types.transition_time(
                                self.transition_time
                            ),
                            'sat': 255,
                        }
                        set_light_multiple(self.bridge, light.light_id, data)

                    if time_out and \
                       time.time() - begin + self.sleep_time >= time_out:
                        raise StopIteration

                    time.sleep(self.sleep_time)

        except StopIteration:
            if time_out:
                time_left = time.time() - begin - time_out
                if time_left > 0:
                    time.sleep(time_left)
