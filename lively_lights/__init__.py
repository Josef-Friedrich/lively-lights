"""Control the hue lamps from Philips using Python."""

from lively_lights import environment
from lively_lights import scenes
from lively_lights.cli import get_parser
from lively_lights.environment import ReachableLights
from lively_lights.phue import Bridge
import configparser
import contextlib
import daemon
import evdev
import lockfile
import os


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

args = None


evdev
"""Import the evdev package."""


def lights_info(bridge):
    for light in bridge.lights:
        info = '{}: {}'.format(light.light_id, light.name)
        print(info)


class Configuration(object):

    def __init__(self, config_file_path=None,
                 config_environ_prefix=None):
        """
        :param str config_file_path: The path of the configuration file.
          The default value is `~/.lively-lights.ini`.
        :param str config_environ_prefix: The environment variable prefix
          `lively_lights` should look for configuration, by default
          `LIVELY_LIGHTS_`.
        """

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
            try:
                converted_value = float(value)
                return converted_value
            except ValueError:
                return value

        else:
            raise ValueError('Configuration value could not be found '
                             '(section “{}” key “{}”).'.format(section, key))


class Hue(object):
    """Convenience class to bundle all configuration and setup in one
    object."""

    def __init__(self, ip=None, username=None,
                 config_file_path=None,
                 config_environ_prefix=None, verbosity_level=0,
                 colorize_output=False):
        """
        :param str ip: The IP address of the Hue bridge. IP address as dotted
          quad.
        :param str username: The username to authenticate against the Hue
          bridge.
        :param str config_file_path: The path of the configuration file.
          The default value is `~/.lively-lights.ini`.
        :param str config_environ_prefix: The environment variable prefix
          `lively_lights` should look for configuration, by default
          `LIVELY_LIGHTS_`.
        """

        self.config = Configuration(config_file_path, config_environ_prefix)
        """:class:`lively_lights.Configuration`"""

        if not ip:
            ip = self.config.get('bridge', 'ip')

        if not username:
            username = self.config.get('bridge', 'username')

        self.bridge = Bridge(ip, username, verbosity_level=verbosity_level,
                             colorize_output=colorize_output)
        """:class:`lively_lights.phue.Bridge`"""


def main():
    global args
    args = get_parser().parse_args()

    config = Configuration(config_file_path=args.config_file)
    day_night = environment.DayNight(
        config.get('location', 'latitude'),
        config.get('location', 'longitude'),
        config.get('location', 'timezone'),
        config.get('location', 'elevation'),
    )
    if args.subcommand == 'info' and args.info == 'daynight':
        print(day_night.overview())
        return

    hue = Hue(ip=args.ip, username=args.username,
              config_file_path=args.config_file,
              verbosity_level=args.verbosity_level,
              colorize_output=args.colorize)

    reachable_lights = ReachableLights(
        hue.bridge,
        day_night,
        not_at_night=args.not_at_night,
        not_during_daytime=args.not_during_daytime,
        not_host_up=args.not_host_up,
        turn_off=args.turn_off,
    )

    if args.lights:
        reachable_lights.light_ids = args.lights

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
                reachable_lights,
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
                reachable_lights,
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
