"""A collection of scenes."""

from lively_lights import _random as random
from lively_lights._utils import set_light_multiple
from lively_lights import types
from random import randint, shuffle
import threading
import time
import sys
import yaml


class Launcher(object):

    """
    Launch scenes.

    :param bridge: The bridge object
    :type bridge: lively_lights.phue.Bridge

    :param reachable_lights: An object containing the specified and
      reachable lights.
    :type reachable_lights: lively_lights.ReachableLights

    :param list scene_configs: A list of `scene_config` lists.

    .. code-block:: python

        scene_configs = [
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

    :param string scene_configs_file: The file path of a yaml file containing
      the scene configurations.

    .. code-block:: yaml

        - title: Rainbow
          description: Cycle between three colors
          scene_name: sequence
          duration: 3
          properties:
            brightness: 254
            hue_sequence:
            - 0
            - 40000
            - 30000
            sleep_time: 2
            transition_time: 1

        - title: Breath
          description: Breathing colors
          scene_name: breath
          duration: 3
          properties:
              time_range:
              - 1
              - 2

    """

    def __init__(self, bridge, reachable_lights, scene_configs=None,
                 scene_configs_file=None, verbosity_level=0):
        self.bridge = bridge
        """The bridge object: :class:`lively_lights.phue.Bridge`"""
        self.reachable_lights = reachable_lights
        """A reachable lights object :class:`lively_lights.ReachableLights`:"""
        self.verbosity_level = verbosity_level
        """The verbosity level."""
        self.scenes = []
        """A list of scenes :class:`lively_lights.scenes.Scene`"""
        if scene_configs:
            for scene_config in scene_configs:
                self.scenes.append(self._init_scene(scene_config))
        if scene_configs_file:
            scene_configs = self._read_yaml(scene_configs_file)
            for scene_config in scene_configs:
                self.scenes.append(self._init_scene(scene_config))

    @staticmethod
    def _read_yaml(yaml_file):
        with open(yaml_file, 'r') as stream:
            return yaml.load(stream)

    @staticmethod
    def _get_scene_class(scene_name):
        class_name = 'Scene{}'.format(scene_name.title())
        return getattr(sys.modules[__name__], class_name)

    def _init_scene(self, scene_config):
        Scene = self._get_scene_class(scene_config['scene_name'])
        scene = Scene(self.bridge, self.reachable_lights)
        if 'title' in scene_config:
            scene.title = scene_config['title']
        if 'description' in scene_config:
            scene.description = scene_config['description']
        if 'duration' in scene_config:
            scene.duration = scene_config['duration']
        try:
            scene.get_properties_from_dict(scene_config['properties'])
            return scene
        except ValueError:
            raise ValueError('Invalid scene config: {}'.format(scene_config))

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
        scene = self._init_scene(scene_config)
        scene.start(scene_config['duration'])

    def _start_scene(self, scene, duration=None):
        scene.scene_reporter(self.verbosity_level)
        scene.start(duration)

    def _launch_randomized(self, duration=None):
        scenes_indexes = list(range(len(self.scenes)))
        shuffle(scenes_indexes)
        for index in scenes_indexes:
            self._start_scene(self.scenes[index], duration)

    def _launch_sorted(self, duration=None):
        for scene in self.scenes:
            self._start_scene(scene, duration)

    def _launch(self, randomized=False, duration=None):
        if randomized:
            self._launch_randomized(duration)
        else:
            self._launch_sorted(duration)

    def launch(self, randomized=False, endless=False, duration=None):
        if endless:
            while True:
                self._launch(randomized, duration)
        else:
            self._launch(randomized, duration)


class Scene(object):

    """
    :param reachable_lights: An object containing the specified and
      reachable lights.
    :type reachable_lights: lively_lights.ReachableLights
    """

    name = None
    """The name of the scene class."""

    properties = {}
    """
    A dictonary of properties. Property names are the keys.

    .. code-block:: python

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
    """

    title = None
    """The title of the scene instance."""

    description = None
    """The description of the scene instance."""

    duration = None
    """Default duration of the scene instance. This value is used in the
    method :class:`lively_lights.scenes.Scene.start`."""

    actual_duration = None
    """The method :class:`lively_lights.scenes.Scene.start` measures the
    actual time taken and stores the result in this attribute."""

    def __init__(self, bridge, reachable_lights, **kwargs):
        self.bridge = bridge
        self.reachable_lights = reachable_lights

        for key, value in kwargs.items():
            if key in self.properties:
                setattr(self, key, value)
            else:
                raise ValueError('Property “{}” is not allowed.'.format(key))

        self._set_defaults()
        self._validate()

    def get_properties_from_args(self, args):
        for property, value in self.properties.items():
            if hasattr(args, property) and getattr(args, property):
                setattr(self, property, getattr(args, property))
        self._set_defaults()
        self._validate()

    def get_properties_from_dict(self, dictionary):
        for key, value in dictionary.items():
            if key not in self.properties:
                raise ValueError('Property “{}” is not allowed.'.format(key))
        for property, value in self.properties.items():
            if property in dictionary:
                setattr(self, property, dictionary[property])
        self._set_defaults()
        self._validate()

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

    def _run(self, duration=None):
        """Should be overwritten."""
        pass

    def start(self, duration=None):
        if duration:
            _duration = duration
        elif self.duration:
            _duration = self.duration
        else:
            _duration = None
        begin = time.time()
        self._run(duration=_duration)
        end = time.time()
        self.actual_duration = end - begin

    def scene_reporter(self, verbosity_level):
        if verbosity_level > 0:
            out = []
            out.append('name: {}'.format(self.name))
            for property, _ in self.properties.items():
                out.append('{}: {}'.format(property, getattr(self, property)))

            print('\n'.join(out))


class SceneBreath(Scene):

    name = 'breath'

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
                random.brightness(max=99),
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
                   time.time() + time_span > self._time_to_end:
                    break
                data = {
                    'hue': randint(*self.hue_range),
                    'transitiontime': types.transition_time(time_span - 0.2),
                    'bri': randint(*self.brightness_range),
                    'sat': 254,
                }
                set_light_multiple(self.bridge, light_id, data)
                time.sleep(time_span)
            else:
                break

    def _run(self, duration=None):
        refresh_interval = self.reachable_lights.refresh_interval
        if duration:
            self._time_to_end = time.time() + duration
        while True:
            if self._time_to_end and self._time_to_end <= time.time():
                break

            for light in self.reachable_lights.get_light_objects():
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

            if self._time_to_end and \
               time.time() + refresh_interval > self._time_to_end:
                sleep_time = self._time_to_end - time.time()
            else:
                sleep_time = self.reachable_lights.refresh_interval
            time.sleep(sleep_time)


class ScenePendulum(Scene):

    name = 'pendulum'

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

        if self.transition_time > self.sleep_time:
            raise ValueError('transition_time should be less than sleep_time')

    def _distribute_lights(self):
        light_ids = self.reachable_lights.get_light_ids()
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

    def _run(self, duration=None):
        begin = time.time()

        if duration and duration <= self.sleep_time:
            self.sleep_time = duration / 2
            self.transition_time = self.sleep_time * 0.2

        while True:
            self._set_light_group(self.lights1, self.color1)
            self._set_light_group(self.lights2, self.color2)
            if duration and \
               time.time() - begin + self.sleep_time >= duration:
                break
            time.sleep(self.sleep_time)
            self._set_light_group(self.lights1, self.color2)
            self._set_light_group(self.lights2, self.color1)
            if duration and \
               time.time() - begin + self.sleep_time >= duration:
                break
            time.sleep(self.sleep_time)

        if duration:
            time_left = duration - (time.time() - begin)
            if time_left > 0:
                time.sleep(time_left)


class SceneSequence(Scene):

    name = 'sequence'

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

        if self.transition_time > self.sleep_time:
            raise ValueError('transition_time should be less than sleep_time')

    def _run(self, duration=None):
        begin = time.time()

        if duration and duration <= self.sleep_time:
            self.sleep_time = duration / 2
            self.transition_time = self.sleep_time * 0.2
        try:
            while True:
                for hue in self.hue_sequence:
                    for light in self.reachable_lights.get_light_objects():
                        data = {
                            'hue': hue,
                            'bri': self.brightness,
                            'transitiontime': types.transition_time(
                                self.transition_time
                            ),
                            'sat': 255,
                        }
                        set_light_multiple(self.bridge, light.light_id, data)

                        if duration and \
                           time.time() - begin + self.sleep_time >= duration:
                            raise StopIteration

                    time.sleep(self.sleep_time)

        except StopIteration:
            if duration:
                time_left = duration - (time.time() - begin)
                if time_left > 0:
                    time.sleep(time_left)
