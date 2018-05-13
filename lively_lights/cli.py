"""The command line interface provided by argparse."""

import argparse


def get_parser():
    parser = argparse.ArgumentParser(
        description='Control the hue lamps from Philips using Python.',
    )

    parser.add_argument(
        '-c', '--config-file',
        help='Path to configuration file',
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

    return parser
