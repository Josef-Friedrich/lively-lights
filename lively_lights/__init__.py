#! /usr/bin/env python3

"""Control the hue lamps from Philips using Python."""

from lively_lights import _random as random
from multiprocessing import Process, Queue
from phue import Bridge
from random import randint
import argparse
import astral
import contextlib
import daemon
import lockfile
import os
import signal
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
    if args.verbose:
        print('{}{}'.format(light_id, data))
    return bridge.request(
        mode='PUT',
        address='/api/{}/lights/{}/state'.format(bridge.username, light_id),
        data=data,
    )


class Configuration(object):

    def __init__(self, config_file_path='~/.lively-lights.ini',
                 config_environ_prefix='LIVELY_LIGHTS'):
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
                 config_file_path='~/.lively-lights.ini',
                 config_environ_prefix='LIVELY_LIGHTS'):
        self.config = Configuration(config_file_path, config_environ_prefix)

        if not ip:
            ip = self.config.get('bridge', 'ip')

        if not username:
            username = self.config.get('bridge', 'username')

        self.bridge = Bridge(ip, username)
        self.lights = Lights(self.bridge)


def get_reachable_lights(bridge):
    lights = []
    for light in bridge.lights:
        if light.reachable:
            lights.append(light)
    return lights


class Lights(object):

    def __init__(self, bridge, light_ids=None, detect_reachable=False,
                 refresh_interval=60):
        """
        :param int interval: Search every n seconds for new lights
        """
        self.bridge = bridge
        self.light_ids = light_ids
        self.detect_reachable = detect_reachable
        self.refresh_interval = refresh_interval
        self._last_refresh = None
        self._reachable_lights = None

    def _get_reachable(self, light_ids=None):
        lights = []

        if self._reachable_lights and \
           self.refresh_interval and \
           self._last_refresh and \
           time.time() - self._last_refresh < self.refresh_interval:
            return self._reachable_lights
        else:  # refresh
            self._last_refresh = time.time()
            if light_ids:
                for light_id in light_ids:
                    if self.bridge[light_id].reachable:
                        lights.append(self.bridge[light_id])
            else:
                for light in self.bridge.lights:
                    if light.reachable:
                        lights.append(light)

            self._reachable_lights = lights

            return lights

    def _convert_to_light_objects(self, light_ids):
        lights = []
        for light_id in light_ids:
            lights.append(self.bridge[light_id])
        return lights

    def list(self):
        if self.detect_reachable:
            if self.light_ids:
                return self._get_reachable(self.light_ids)
            else:
                return self._get_reachable()
        else:  # not detect_reachable
            if self.light_ids:
                return self._convert_to_light_objects(self.light_ids)
            else:
                return self.bridge.lights


class SceneBreath(object):

    def __init__(self, bridge, lights='auto',
                 hue_range=(randint(0, 32766), randint(32767, 65535)),
                 time_range=(randint(1, 4), randint(5, 8)),
                 bri_range=(randint(1, 100), randint(101, 255))):

        self.queue = Queue()
        self.bridge = bridge
        self.lights = lights
        self.hue_range = hue_range
        self.time_range = time_range
        self.bri_range = bri_range
        self.process = None

    @staticmethod
    def _set_light(bridge, light_id, hue_range, time_range, bri_range):
        while True:
            transitiontime = randint(*time_range)
            data = {
                'hue': randint(hue_range[0], hue_range[1]),
                'transitiontime': transitiontime * 10,
                'bri': randint(*bri_range),
                'sat': 254,
            }
            set_light_multiple(bridge, light_id, data)
            time.sleep(transitiontime + 0.2)

    @staticmethod
    def _light_process_manager(queue, bridge, hue_range, time_range,
                               bri_range):
        processes = {}
        while True:
            for light in bridge.lights:

                lid = light.light_id

                if lid in processes and processes[lid].is_alive and \
                   not light.reachable:
                    processes[lid].terminate()

                elif lid not in processes and light.reachable:
                    p = Process(
                        target=SceneBreath._set_light,
                        args=(
                            bridge,
                            lid,
                            hue_range,
                            time_range,
                            bri_range,
                        ),
                    )
                    p.start()
                    processes[lid] = p
                    queue.put(p.pid)

            time.sleep(10)

    def start(self, duration=None):
        p = Process(
            target=SceneBreath._light_process_manager,
            args=(
                self.queue,
                self.bridge,
                self.hue_range,
                self.time_range,
                self.bri_range,
            ),
        )
        p.start()
        self.queue.put(p.pid)

        if duration:
            time.sleep(duration)
            while self.queue.qsize():
                pid = self.queue.get()
                os.kill(pid, signal.SIGTERM)

    def stop(self):
        while self.queue.qsize():
            pid = self.queue.get()
            os.kill(pid, signal.SIGTERM)


class ScenePendulum(object):

    def __init__(self, bridge, lights, color_1=None, color_2=None,
                 lights_1=None, lights_2=None, sleep_time=None,
                 transition_time=None):
        self.bridge = bridge
        self.lights = lights
        self.color_1 = color_1
        self.color_2 = color_1
        self.lights_1 = lights_1
        self.lights_2 = lights_2
        self.sleep_time = sleep_time
        self.transition_time = transition_time

    def _distribute_lights(self):
        lights = self.lights.list()
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

    def __init__(self, bridge, lights, brightness=None, hue_sequence=None,
                 sleep_time=None, transition_time=None):
        self.bridge = bridge
        self.lights = lights
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
                for light in self.lights.list():
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


def parse_args():
    parser = argparse.ArgumentParser(
        description='Control the hue lamps from Philips using Python.',
    )

    parser.add_argument(
        '-d', '--daemonize',
        action='store_true',
        help='Fork the process in the background.',
    )

    parser.add_argument(
        '-i', '--ip',
        type=str,
        help='IP address as dotted quad.',
    )

    parser.add_argument(
        '-l', '--lights',
        nargs='+',
        help='Light ids (e. g: -l 1 2 3)',
    )

    parser.add_argument(
        '-u', '--username',
        type=str,
        help='The username to login.',
    )

    parser.add_argument(
        '-r', '--reachable',
        action='store_true',
        help='Detect and use only reachable lights.',
    )

    parser.add_argument(
        '-t', '--time-out',
        type=float,
        help='Set time out in seconds.',
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Make output more verbose.',
    )

    subparsers = parser.add_subparsers(
        dest='scene',
        help='Lively scenes',
    )

    subparsers.required = True

    breath = subparsers.add_parser(
        'breath',
        help='Fade the lights smoothly up and down, so it seems that they '
        'were breathing.'
    )

    breath.add_argument(
        '-b', '--brightness-range',
        nargs=2,
        help='Two brightness values (e. g. 10 255).'
    )

    # 	-H, --hue-range
    # 		Two hue color values (e. g. 23461:40123)
    #
    # 	-l, --lights
    # 		Lights to use (comma seperated numbers, e. g.: 1,2,3).
    #
    # 	-t, --time-range
    # 		A time range in seconds separated by a colon.
    #

    pendulum = subparsers.add_parser(
        'pendulum',
        help='Switch two group of lights between twocolors.',
    )

    pendulum.add_argument(
        '-c1', '--color1',
        nargs=1,
        help='Hue color value (0 - 65535) for lights group 1.',
    )

    pendulum.add_argument(
        '-c2', '--color2',
        type=int,
        help='Hue color value (0 - 65535) for lights group 2.',
    )

    pendulum.add_argument(
        '-l1', '--lights1',
        type=int,
        help='Lights group 1 (spaces seperated numbers, e. g.: 4 5 6).',
    )

    pendulum.add_argument(
        '-l2', '--lights2',
        nargs='+',
        help='Lights group 2 (spaces seperated numbers, e. g.: 4 5 6).',
    )

    pendulum.add_argument(
        '-s', '--sleep-time',
        type=float,
        help='Time in seconds to switch between the two lights groups.',
    )

    pendulum.add_argument(
        '-t', '--transition-time',
        type=float,
        help='Transition time for the color change (-t 10 = one second).',
    )

    sequence = subparsers.add_parser(
        'sequence',
        help='Change all lights at the same time in a certain sequence.',
    )

    sequence.add_argument(
        '-b', '--brightness',
        type=int,
        help='Brightness of the lights (0 - 255)',
    )

    sequence.add_argument(
        '-H', '--hue-sequence',
        nargs='+',
        help='A sequence of hue color values (0 - 65535).',
    )

    sequence.add_argument(
        '-s', '--sleep-time',
        type=float,
        help='Time between the color changes in seconds.',
    )

    sequence.add_argument(
        '-t', '--transition-time',
        type=float,
        help='Transition time in seconds.',
    )

    subparsers.add_parser(
        'daynight',
        help='Print the current sunset and sunrise times.'
    )

    return parser.parse_args()


def main():
    global args
    args = parse_args()

    config = Configuration()
    if args.scene == 'daynight':
        day_night = DayNight(config)
        day_night.overview()
        return

    hue = Hue(ip=args.ip, username=args.username)

    if args.daemonize:
        ctx_mgr = daemon.DaemonContext(
            pidfile=lockfile.FileLock('/tmp/hue.pid'),
        )
    else:
        ctx_mgr = contextlib.suppress()

    with ctx_mgr:
        if args.scene == 'pendulum':
            scene = ScenePendulum(
                hue.bridge,
                hue.lights,
                color_1=args.color1,
                color_2=args.color2,
                lights_1=args.lights1,
                lights_2=args.lights2,
                sleep_time=args.sleep_time,
                transition_time=args.transition_time,
            )

        elif args.scene == 'sequence':
            scene = SceneSequence(
                hue.bridge,
                hue.lights,
                args.brightness,
                args.hue_sequence, args.sleep_time,
                args.transition_time
            )

        scene.start(time_out=args.time_out)


if __name__ == '__main__':
    main()
