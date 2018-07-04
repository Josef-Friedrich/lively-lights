#! /usr/bin/env python3

"""Control the hue lamps from Philips using Python."""


from lively_lights import scenes
from lively_lights.cli import get_parser
from lively_lights.phue import Bridge
import astral
import configparser
import contextlib
import daemon
import datetime
import lockfile
import os
import time


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


def lights_info(bridge):
    for light in bridge.lights:
        info = '{}: {}'.format(light.light_id, light.name)
        print(info)


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

    def list_light_ids(self):
        out = []
        for light in self.list():
            out.append(light.light_id)
        return(out)


def main():
    global args
    args = get_parser().parse_args()

    config = Configuration(config_file_path=args.config_file)
    if args.subcommand == 'info' and args.info == 'daynight':
        day_night = DayNight(config)
        day_night.overview()
        return

    hue = Hue(ip=args.ip, username=args.username,
              config_file_path=args.config_file,
              verbosity_level=args.verbosity_level,
              colorize_output=args.colorize)

    if args.subcommand == 'info' and args.info == 'lights':
        lights_info(hue.bridge)
        return

    if args.daemonize:
        ctx_mgr = daemon.DaemonContext(
            pidfile=lockfile.FileLock('/tmp/hue.pid'),
        )
    else:
        ctx_mgr = contextlib.suppress()

    with ctx_mgr:
        if args.subcommand == 'scene':
            if args.scene == 'breath':
                Scene = scenes.SceneBreath
            elif args.scene == 'pendulum':
                Scene = scenes.ScenePendulum
            elif args.scene == 'sequence':
                Scene = scenes.SceneSequence

            scene = Scene(
                hue.bridge,
                hue.reachable_lights,
            )
            scene.get_properties_from_args(args)
            scene.scene_reporter(args.verbosity_level)
            scene.start(duration=args.duration)
            if args.verbosity_level > 0 and args.duration and \
               scene.actual_duration:
                print('duration: {}'.format(scene.duration))
                print('actual_duration: {0:.2f}'.format(scene.actual_duration))

        elif args.subcommand == 'launch':
            launcher = scenes.Launcher(
                hue.bridge,
                hue.reachable_lights,
                scene_configs_file=args.yamlfile,
                verbosity_level=args.verbosity_level
            )
            launcher.launch(
                randomized=args.randomized,
                endless=args.endless,
                duration=args.duration,
            )


if __name__ == '__main__':
    main()
