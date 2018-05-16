
"""A collection of scenes."""

from lively_lights import _random as random
from lively_lights._utils import set_light_multiple
from random import randint
import threading
import time


class Scene(object):

    properties = []

    def __init__(self, bridge, reachable_lights, **kwargs):

        self.bridge = bridge
        self.reachable_lights = reachable_lights

        for key, value in kwargs.items():
            if key in self.properties:
                setattr(self, key, value)
            else:
                raise ValueError('Property “{}” is not allowed.'.format(key))

    def get_properties_from_args(self, args):
        for property in self.properties:
            if hasattr(args, property):
                setattr(self, property, getattr(args, property))

    def _setup(self):
        """Should be overwritten."""
        pass

    def start(self, time_out=None):
        """Should be overwritten."""
        pass


class SceneBreath(object):

    def __init__(self, bridge, reachable_lights,
                 hue_range=None,
                 time_range=None,
                 bri_range=None):

        self.bridge = bridge
        self.reachable_lights = reachable_lights
        self.hue_range = hue_range
        self.time_range = time_range
        self.bri_range = bri_range
        self._threads = {}
        self._time_to_end = None

    def _setup(self):
        if not self.hue_range:
            self.hue_range = (random.hue(max=32766), random.hue(min=32767))

        if not self.time_range:
            self.time_range = (
                random.time(min=1, max=4, decimal_places=1),
                random.time(min=4, max=8, decimal_places=1),
            )

        if not self.bri_range:
            self.bri_range = (
                random.brightness(max=100),
                random.brightness(min=100),
            )

    def _set_light(self, light_id):
        while True:
            if self.reachable_lights.is_reachable(light_id):
                transitiontime = randint(
                    self.time_range[0] * 10,
                    self.time_range[1] * 10
                )
                if self._time_to_end and \
                   time.time() - transitiontime / 10 > self._time_to_end:
                    break
                data = {
                    'hue': randint(*self.hue_range),
                    'transitiontime': transitiontime,
                    'bri': randint(*self.bri_range),
                    'sat': 254,
                }
                set_light_multiple(self.bridge, light_id, data)
                time.sleep(transitiontime / 10 + 0.2)
            else:
                break

    def start(self, time_out=None):
        self._setup()
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


class ScenePendulum(object):

    def __init__(self, bridge, reachable_lights, color_1=None, color_2=None,
                 lights_1=None, lights_2=None, sleep_time=None,
                 transition_time=None):
        self.bridge = bridge
        self.reachable_lights = reachable_lights
        self.color_1 = color_1
        self.color_2 = color_1
        self.lights_1 = lights_1
        self.lights_2 = lights_2
        self.sleep_time = sleep_time
        self.transition_time = transition_time

    def _distribute_lights(self):
        lights = self.reachable_lights.list()
        random.shuffle(lights)
        count = len(lights)
        half = int(count / 2)
        return (lights[0:half], lights[half:])

    def _setup(self):
        if not self.color_1:
            self.color_1 = random.hue()

        if not self.color_2:
            self.color_2 = random.hue()

        self.lights_1, self.lights_2 = self._distribute_lights()

        if not self.sleep_time:
            self.sleep_time = random.time(4, 8)

        if not self.transition_time:
            self.transition_time = random.time(1, 3, is_transition_time=True)

    def _set_light_group(self, lights, hue):
        for light in lights:
            data = {
                'hue': hue,
                'bri': 254,
                'transitiontime': self.transition_time,
                'sat': 254,
            }
            set_light_multiple(self.bridge, light.light_id, data)

    def start(self, time_out=None):
        self._setup()
        begin = time.time()
        while True:
            if time_out and \
               time.time() - begin + self.sleep_time * 2 >= time_out:
                break
            self._set_light_group(self.lights_1, self.color_1)
            self._set_light_group(self.lights_2, self.color_2)
            time.sleep(self.sleep_time)
            self._set_light_group(self.lights_1, self.color_2)
            self._set_light_group(self.lights_2, self.color_1)
            time.sleep(self.sleep_time)

        if time_out:
            time_left = time.time() - begin - time_out
            if time_left > 0:
                time.sleep(time_left)


class SceneSequence(object):

    def __init__(self, bridge, reachable_lights, brightness=None,
                 hue_sequence=None,
                 sleep_time=None, transition_time=None):
        self.bridge = bridge  #: The bridge object
        self.reachable_lights = reachable_lights  #: All reachable lights
        self.brightness = brightness
        self.hue_sequence = hue_sequence
        self.sleep_time = sleep_time
        self.transition_time = transition_time

    def _setup(self):
        if not self.brightness:
            self.brightness = random.brightness(min=100)

        if not self.hue_sequence:
            self.hue_sequence = (
                random.hue(),
                random.hue(),
                random.hue(),
                random.hue(),
            )

        if not self.sleep_time:
            self.sleep_time = random.time(4, 8)

        if not self.transition_time:
            self.transition_time = random.time(1, 3, is_transition_time=True)

    def start(self, time_out=None):
        self._setup()
        begin = time.time()
        try:
            while True:
                for hue in self.hue_sequence:
                    for light in self.reachable_lights.list():
                        data = {
                            'hue': hue,
                            'bri': self.brightness,
                            'transitiontime': self.transition_time,
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
