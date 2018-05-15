#! /usr/bin/env python3

"""Control the hue lamps from Philips using Python."""

from lively_lights import _random as random
from lively_lights.phue import Bridge
from lively_lights.cli import get_parser
import threading
from random import randint
import astral
import contextlib
import daemon
import lockfile
import os
import time
import configparser
import datetime


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

args = None


class DayNight(object):

    def __init__(self, config):
        self.location = astral.Location((
            'name',
            'region',
            float(config.get('location', 'latitude')),
            float(config.get('location', 'longitude')),
            config.get('location', 'timezone'),
            float(config.get('location', 'elevation')),
        ))

    def sunrise(self):
        return self.location.sunrise()

    def sunset(self):
        return self.location.sunset()

    def is_day(self):
        sunrise = self.sunrise()
        return sunrise < datetime.datetime.now(sunrise.tzinfo) < self.sunset()

    def is_night(self):
        return not self.is_day()

    def overview(self):
        sun = self.location.sun()
        print('Dawn:    {}'.format(sun['dawn']))
        print('Sunrise: {}'.format(sun['sunrise']))
        print('Noon:    {}'.format(sun['noon']))
        print('Sunset:  {}'.format(sun['sunset']))
        print('Dusk:    {}'.format(sun['dusk']))


def light_info(light, attr):
    attr_strings = []
    for a in attr:
        attr_strings.append('{}: {}'.format(a, getattr(light, a)))

    info = '{}: {} ({})'.format(light.light_id,
                                light.name,
                                '; '.join(attr_strings))

    print(info)


def set_light_multiple(bridge, light_id, data):
    return bridge.request(
        mode='PUT',
        address='/api/{}/lights/{}/state'.format(bridge.username, light_id),
        data=data,
    )


class Configuration(object):

    def __init__(self, config_file_path=None,
                 config_environ_prefix=None):

        if not config_file_path:
            config_file_path = '~/.lively-lights.ini'
        if not config_environ_prefix:
            config_environ_prefix = 'LIVELY_LIGHTS'

        self.config_path = os.path.expanduser(config_file_path)
        self.environ_prefix = config_environ_prefix
        if os.path.exists(self.config_path):
            self.config = configparser.ConfigParser()
            self.config.read(self.config_path)

    def _envrion_key(self, section, key):
        return '{}_{}_{}'.format(self.environ_prefix, section.upper(),
                                 key.upper())

    def get(self, section, key):
        envrion_key = self._envrion_key(section, key)
        if envrion_key in os.environ:
            return os.environ[envrion_key]
        elif section in self.config and key in self.config[section]:
            return self.config[section][key]


class Hue(object):

    def __init__(self, ip=None, username=None,
                 config_file_path=None,
                 config_environ_prefix=None, verbosity_level=0,
                 colorize_output=False):
        self.config = Configuration(config_file_path, config_environ_prefix)

        if not ip:
            ip = self.config.get('bridge', 'ip')

        if not username:
            username = self.config.get('bridge', 'username')

        self.bridge = Bridge(ip, username, verbosity_level=verbosity_level,
                             colorize_output=colorize_output)
        self.reachable_lights = ReachableLights(self.bridge)


def get_reachable_lights(bridge):
    lights = []
    for light in bridge.lights:
        if light.reachable:
            lights.append(light)
    return lights


class ReachableLights(object):

    def __init__(self, bridge, light_ids=None, refresh_interval=60):
        """
        :param int interval: Search every n seconds for new lights
        """
        self.bridge = bridge
        self.light_ids = light_ids
        self.refresh_interval = refresh_interval
        self._lights_refresh_state = {}

    def _get_reachable(self, light_ids=None):
        lights = []

        if light_ids:
            for light_id in light_ids:
                if self.is_reachable(light_id):
                    lights.append(self.bridge[light_id])
        else:
            for light in self.bridge.lights:
                if self.is_reachable(light.light_id):
                    lights.append(light)

        return lights

    def is_reachable(self, light_id):
        state = self._lights_refresh_state
        if light_id in state and \
           time.time() - state[light_id][0] < self.refresh_interval:
            return state[light_id][1]
        else:
            reachable = self.bridge[light_id].reachable
            state[light_id] = (time.time(), reachable)
            return reachable

    def list(self):
        if self.light_ids:
            return self._get_reachable(self.light_ids)
        else:
            return self._get_reachable()


class SceneBreath(object):

    def __init__(self, bridge, reachable_lights,
                 hue_range=(randint(0, 32766), randint(32767, 65535)),
                 time_range=(randint(1, 4), randint(5, 8)),
                 bri_range=(randint(1, 100), randint(101, 255))):

        self.bridge = bridge
        self.reachable_lights = reachable_lights
        self.hue_range = hue_range
        self.time_range = time_range
        self.bri_range = bri_range
        self._threads = {}

    @staticmethod
    def _set_light(bridge, reachable_lights, light_id, hue_range, time_range,
                   bri_range):
        while True:
            if reachable_lights.is_reachable(light_id):
                transitiontime = randint(*time_range)
                data = {
                    'hue': randint(hue_range[0], hue_range[1]),
                    'transitiontime': transitiontime * 10,
                    'bri': randint(*bri_range),
                    'sat': 254,
                }
                set_light_multiple(bridge, light_id, data)
                time.sleep(transitiontime + 0.2)
            else:
                break

    def start(self, time_out=None):
        while True:
            for light in self.reachable_lights.list():
                if light.light_id not in self._threads or \
                   not self._threads[light.light_id].is_alive():
                    t = threading.Thread(
                        target=SceneBreath._set_light,
                        args=(
                            self.bridge,
                            self.reachable_lights,
                            light.light_id,
                            self.hue_range,
                            self.time_range,
                            self.bri_range,
                        ),
                    )
                    t.start()
                    self._threads[light.light_id] = t


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
            self._set_light_group(self.lights_1, self.color_1)
            self._set_light_group(self.lights_2, self.color_2)
            time.sleep(self.sleep_time)
            self._set_light_group(self.lights_1, self.color_2)
            self._set_light_group(self.lights_2, self.color_1)
            time.sleep(self.sleep_time)

            if time_out and time.time() - begin > time_out:
                break


class SceneSequence(object):

    def __init__(self, bridge, reachable_lights, brightness=None,
                 hue_sequence=None,
                 sleep_time=None, transition_time=None):
        self.bridge = bridge
        self.reachable_lights = reachable_lights
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

                time.sleep(self.sleep_time)

            if time_out and time.time() - begin > time_out:
                break


def main():
    global args
    args = get_parser().parse_args()

    config = Configuration(config_file_path=args.config_file)
    if args.subcommand == 'info':
        if args.info == 'daynight':
            day_night = DayNight(config)
            day_night.overview()
            return

    hue = Hue(ip=args.ip, username=args.username,
              config_file_path=args.config_file, verbosity_level=args.verbose,
              colorize_output=args.colorize)

    if args.daemonize:
        ctx_mgr = daemon.DaemonContext(
            pidfile=lockfile.FileLock('/tmp/hue.pid'),
        )
    else:
        ctx_mgr = contextlib.suppress()

    with ctx_mgr:
        if args.subcommand == 'scene':
            if args.scene == 'breath':
                scene = SceneBreath(
                    hue.bridge,
                    hue.reachable_lights,
                )

            elif args.scene == 'pendulum':
                scene = ScenePendulum(
                    hue.bridge,
                    hue.reachable_lights,
                    color_1=args.color1,
                    color_2=args.color2,
                    lights_1=args.lights1,
                    lights_2=args.lights2,
                    sleep_time=args.sleep_time,
                    transition_time=args.transition_time,
                )

            elif args.subsub == 'sequence':
                scene = SceneSequence(
                    hue.bridge,
                    hue.reachable_lights,
                    args.brightness,
                    args.hue_sequence, args.sleep_time,
                    args.transition_time
                )

        scene.start(time_out=args.time_out)


if __name__ == '__main__':
    main()
