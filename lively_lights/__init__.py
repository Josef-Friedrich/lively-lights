#! /usr/bin/env python3

"""Control the hue lamps from Philips using Python."""


from lively_lights import environment
from lively_lights import scenes
from lively_lights.cli import get_parser
from lively_lights.phue import Bridge
import configparser
import contextlib
import daemon
import lockfile
import os
import time


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

args = None


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
        value = None
        envrion_key = self._envrion_key(section, key)
        if envrion_key in os.environ:
            value = os.environ[envrion_key]
        elif hasattr(self, 'config') and section in self.config and \
                key in self.config[section]:
            value = self.config[section][key]

        if value:
            return value
        else:
            raise ValueError('Configuration value could not be found '
                             '(section “{}” key “{}”).'.format(section, key))


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
    """
    :param bridge: The bridge object
    :type bridge: lively_lights.phue.Bridge

    :param list light_ids: Light IDs to filter the output of the methods
      :class:`lively_lights.ReachableLights.list` and
      :class:`lively_lights.ReachableLights.list_light_ids`

    :param int refresh_interval: Search every n seconds for new lights

    :param bool at_night: Return light IDs only at night.

    :param bool at_day: Return light IDs only at day.

    :param string check_open_port: Check if a host has an open TCP port:
      e. g. 192.168.3.11:22

    :param bool on_open_port: This parameter only takes effect if the parameter
      `check_open_port` is not empty.

    :param string check_ping: Check if a host is pingable. You have to be root
       e. g. 192.168.3.11

    :param bool on_ping: This parameter only takes effect if the parameter
      `check_ping` is not empty.
    """
    def __init__(self, bridge, light_ids=None, refresh_interval=60,
                 at_night=True, at_day=True, check_open_port=None,
                 on_open_port=True, check_ping=None, on_ping=True):

        self.light_ids = light_ids
        """A list of light IDS. """

        self.refresh_interval = refresh_interval
        """Search every n seconds for new lights."""

        self.at_night = at_night
        """Return light IDs only at night."""

        self.at_day = at_day
        """Return light IDs only at day."""

        self.check_open_port = check_open_port
        """Check if a host has an open TCP port: e. g. 192.168.3.11:22"""

        self.on_open_port = on_open_port
        """This parameter only takes effect if the parameter `check_open_port`
        is not empty."""

        self.check_ping = on_ping
        """Check if a host is pingable. You have to be root e. g.
          192.168.3.11"""

        self._current_light_index = 0
        """Needed for the foor loop iteration."""

        self._bridge = bridge
        """The bridge object :class:`lively_lights.phue.Bridge`"""

        self._lights_refresh_state = {}
        """Cache for light states. To avoid querying for reachable lights every
        time.

        .. code-block:: python

            self._lights_refresh_state = {
                1: (1530997150.9431288, True),
                2: (1530997179.6412678, False),
            }

        """

        self._lights = []
        """A list of light objects. Needed for the for loop iteration."""

        self._lights_count = 0
        """Count of reachable lights."""

    def __iter__(self):
        self._lights = self.list()
        self._lights_count = len(self._lights)
        self._current_light_index = 0
        return self

    def __next__(self):
        current = self._current_light_index
        self._current_light_index += 1
        if current >= self._lights_count:
            raise StopIteration
        return self._lights[current]

    def _get_reachable(self, light_ids=None):
        lights = []

        if light_ids:
            for light_id in light_ids:
                if self.is_reachable(light_id):
                    lights.append(self._bridge[light_id])
        else:
            for light in self._bridge.lights:
                if self.is_reachable(light.light_id):
                    lights.append(light)

        return lights

    def is_reachable(self, light_id):
        state = self._lights_refresh_state
        if light_id in state and \
           time.time() - state[light_id][0] < self.refresh_interval:
            return state[light_id][1]
        else:
            reachable = self._bridge[light_id].reachable
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


class ReachableLightsFactory(object):

    def __init__(self, bridge, refresh_interval=60):
        self.bridge = bridge
        self.refresh_interval = refresh_interval

    def get_lights(self, *light_ids):
        return ReachableLights(self.bridge, light_ids, self.refresh_interval)


def main():
    global args
    args = get_parser().parse_args()

    config = Configuration(config_file_path=args.config_file)
    if args.subcommand == 'info' and args.info == 'daynight':
        day_night = environment.DayNight(
            float(config.get('location', 'latitude')),
            float(config.get('location', 'longitude')),
            config.get('location', 'timezone'),
            float(config.get('location', 'elevation')),
        )
        print(day_night.overview())
        return

    hue = Hue(ip=args.ip, username=args.username,
              config_file_path=args.config_file,
              verbosity_level=args.verbosity_level,
              colorize_output=args.colorize)

    if args.lights:
        hue.reachable_lights.light_ids = args.lights

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
