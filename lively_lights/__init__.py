#! /usr/bin/env python3

"""Control the hue lamps from Philips using Python."""

from multiprocessing import Process, Queue
from phue import Bridge
from random import randint
import argparse
import daemon
import os
import signal
import time
import contextlib
import lockfile
import astral
from datetime import date

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

args = None


def sunset_sunrise():
    loc = astral.Location(('Bern', 'Switzerland', 46.95, 7.47, 'Europe/Zurich',
                           510))
    for event, _time in loc.sun(date.today()).items():
        print(event, 'at', _time)


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


def get_reachable_lights(bridge):
    lights = []
    for light in bridge.lights:
        if light.reachable:
            lights.append(light)
    return lights


class Lights(object):

    def __init__(self, bridge, light_ids=None, detect_reachable=False):
        self.bridge = bridge
        self.light_ids = light_ids
        self.detect_reachable = detect_reachable

    def _get_all_reachable(self):
        lights = []
        for light in self.bridge.lights:
            if light.reachable:
                lights.append(light)
        return lights

    def _get_reachable_by_id(self, light_ids):
        lights = []
        for light_id in light_ids:
            if self.bridge[light_id].reachable:
                lights.append(self.bridge[light_id])
        return lights

    def _convert_to_light_objects(self, light_ids):
        lights = []
        for light_id in light_ids:
            lights.append(self.bridge[light_id])
        return lights

    def list(self):
        if self.detect_reachable:
            if self.light_ids:
                return self._get_reachable_by_id(self.light_ids)
            else:
                return self._get_all_reachable()
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
            self.brightness = randint(100, 255)

        if not self.hue_sequence:
            self.hue_sequence = (
                randint(0, 65535),
                randint(0, 65535),
                randint(0, 65535),
                randint(0, 65535),
            )

        if not self.sleep_time:
            self.sleep_time = randint(4, 8)

        if not self.transition_time:
            self.transition_time = randint(1, 3)

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
        '-s', '--switch-time',
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
        'sunset',
        help='Print the current sunset and sunrise times.'
    )

    return parser.parse_args()


def main():
    global args
    args = parse_args()

    if args.scene == 'sunset':
        sunset_sunrise()
        return

    bridge = Bridge(ip=args.ip, username=args.username)
    lights = Lights(bridge, light_ids=args.lights,
                    detect_reachable=args.reachable)

    print(args)

    if args.daemonize:
        ctx_mgr = daemon.DaemonContext(
            pidfile=lockfile.FileLock('/tmp/hue.pid'),
        )
    else:
        ctx_mgr = contextlib.suppress()

    with ctx_mgr:
        if args.scene == 'sequence':

            scene = SceneSequence(bridge, lights, args.brightness,
                                  args.hue_sequence, args.sleep_time,
                                  args.transition_time)

        scene.start(time_out=args.time_out)


if __name__ == '__main__':
    main()
