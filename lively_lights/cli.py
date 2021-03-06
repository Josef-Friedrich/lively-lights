"""The command line interface provided by argparse."""

import argparse
from lively_lights import types


def get_parser():
    parser = argparse.ArgumentParser(
        description='Control the hue lamps from Philips using Python.',
    )

    ##
    # global
    ##

    parser.add_argument(
        '-C', '--colorize',
        action='store_true',
        help='Colorize info and debug output on the command line interface.',
    )

    parser.add_argument(
        '-c', '--config-file',
        help='Path to configuration file',
    )

    parser.add_argument(
        '-D', '--duration',
        type=types.time,
        help='Set the duration of the scene in seconds.',
    )

    parser.add_argument(
        '-d', '--daemonize',
        action='store_true',
        help='Fork the process in the background.',
    )

    parser.add_argument(
        '-H', '--not-host-up',
        default=False,
        help='Do nothing if an external host is up and reachable.',
    )

    parser.add_argument(
        '-i', '--ip',
        type=str,
        help='IP address as dotted quad.',
    )

    parser.add_argument(
        '-l', '--lights',
        type=types.light_id_comma,
        help='Comma separated list of light ids (e. g: -l 1,2,3)',
    )

    parser.add_argument(
        '-n', '--not-at-night',
        action='store_true',
        help='Do nothing at night. In order to pause at the right time, '
        'you have to supply informations of your '
        'location in the configuration file.',
    )

    parser.add_argument(
        '-u', '--username',
        type=str,
        help='The username to login.',
    )

    parser.add_argument(
        '-t', '--turn-off',
        action='store_true',
        help='Turn the lights off if one of the three options ('
        '--not-during-daytime, '
        '--not-at-night, '
        '--not-host-up) is present and takes effect.'
    )

    parser.add_argument(
        '-v', '--verbosity-level',
        default=0,
        action='count',
        help='Make output more verbose.',
    )

    parser.add_argument(
        '-y', '--not-during-daytime',
        action='store_true',
        help='Do nothing during daytime. In order to pause '
        'at the right time, you have to supply informations of your '
        'location in the configuration file.',
    )

    ###########################################################################
    ###########################################################################
    #
    ###########################################################################
    ###########################################################################

    subcommand = parser.add_subparsers(
        dest='subcommand',
        help='Subcommand',
    )

    subcommand.required = True

    ###########################################################################
    # info
    ###########################################################################

    info_parser = subcommand.add_parser('info')
    info = info_parser.add_subparsers(
        dest='info',
        help='Print informations about the current Phillips Hue System'
    )
    info.required = True

    ##
    # info daynight
    ##

    info.add_parser(
        'daynight',
        help='Print the current sunset and sunrise times.'
    )

    info.add_parser(
        'lights',
        help='Print informations about all lights.'
    )

    info.add_parser(
        'groups',
        help='Print informations about all groups.'
    )

    ###########################################################################
    # scene
    ###########################################################################

    scene_parser = subcommand.add_parser('scene')
    scene = scene_parser.add_subparsers(dest='scene')
    scene.required = True

    ##
    # scene breath
    ##

    scene_breath = scene.add_parser(
        'breath',
        help='Fade the lights smoothly up and down, so it seems that they '
        'were breathing.'
    )

    scene_breath.add_argument(
        '-b', '--brightness-range',
        nargs=2,
        type=types.brightness,
        help='Two brightness values (e. g. 10 255).'
    )

    scene_breath.add_argument(
        '-H', '--hue-range',
        nargs=2,
        type=types.hue,
        help='Two hue color values (e. g. 23461 40123).'
    )

    scene_breath.add_argument(
        '-t', '--time-range',
        nargs=2,
        type=types.time,
        help='A time range in seconds separated by a space.'
    )

    ##
    # scene-pendulum
    ##

    scene_pendulum = scene.add_parser(
        'pendulum',
        help='Switch two group of lights between twocolors.',
    )

    scene_pendulum.add_argument(
        '-c1', '--color1',
        type=types.hue,
        help='Hue color value (0 - 65535) for lights group 1.',
    )

    scene_pendulum.add_argument(
        '-c2', '--color2',
        type=types.hue,
        help='Hue color value (0 - 65535) for lights group 2.',
    )

    scene_pendulum.add_argument(
        '-l1', '--lights1',
        nargs='+',
        type=types.light_id,
        help='Lights group 1 (spaces seperated numbers, e. g.: 4 5 6).',
    )

    scene_pendulum.add_argument(
        '-l2', '--lights2',
        nargs='+',
        type=types.light_id,
        help='Lights group 2 (spaces seperated numbers, e. g.: 4 5 6).',
    )

    scene_pendulum.add_argument(
        '-s', '--sleep-time',
        type=types.time,
        help='Time in seconds to switch between the two lights groups.',
    )

    scene_pendulum.add_argument(
        '-t', '--transition-time',
        type=types.time,
        help='Transition time for the color change (-t 10 = one second).',
    )

    ##
    # scene sequence
    ##

    scene_sequence = scene.add_parser(
        'sequence',
        help='Change all lights at the same time in a certain sequence.',
    )

    scene_sequence.add_argument(
        '-b', '--brightness',
        type=types.brightness,
        help='Brightness of the lights (0 - 255)',
    )

    scene_sequence.add_argument(
        '-H', '--hue-sequence',
        nargs='+',
        type=types.hue,
        help='A sequence of hue color values (0 - 65535).',
    )

    scene_sequence.add_argument(
        '-s', '--sleep-time',
        type=types.time,
        help='Time between the color changes in seconds.',
    )

    scene_sequence.add_argument(
        '-t', '--transition-time',
        type=types.time,
        help='Transition time in seconds.',
    )

    ###########################################################################
    # launch
    ###########################################################################

    launch = subcommand.add_parser('launch')

    launch.add_argument(
        'yamlfile',
        help='A yaml file containing the scene configurations.',
    )

    launch.add_argument(
        '-d', '--duration',
        type=float,
        default=0,
        help='Override durations. Play each scene as long as specified '
        '(in seconds).',
    )

    launch.add_argument(
        '-e', '--endless',
        action='store_true',
        help='Play the given senes in a endless loop.',
    )

    launch.add_argument(
        '-r', '--randomized',
        action='store_true',
        help='Launch the scenes in a random order.',
    )

    return parser
