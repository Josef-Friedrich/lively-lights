"""Gather informations about the environment lively lights is running in."""

import astral
import datetime
import pyowm
import socket
from ping3 import ping


def is_host_pingable(host, timeout=3):
    try:
        result = ping(host, timeout=3)
    except PermissionError:
        return None
    if result:
        return True
    else:
        return False


def is_host_reachable(host, port, timeout=3):
    """
    https://stackoverflow.com/a/33117579
    :param string host: ipv4 address
    :param int port: open port
    :param in timeout: Timeout in seconds
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


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

    def _sunrise(self):
        return self.location.sunrise()

    def _sunset(self):
        return self.location.sunset()

    def is_day(self):
        sunrise = self._sunrise()
        return sunrise < datetime.datetime.now(sunrise.tzinfo) < self._sunset()

    def is_night(self):
        return not self.is_day()

    def overview(self):
        sun = self.location.sun()
        print('Dawn:    {}'.format(sun['dawn']))
        print('Sunrise: {}'.format(sun['sunrise']))
        print('Noon:    {}'.format(sun['noon']))
        print('Sunset:  {}'.format(sun['sunset']))
        print('Dusk:    {}'.format(sun['dusk']))


class Weather(object):

    def __init__(self, config):
        owm = pyowm.OWM(config.get('weather', 'openweathermap_api_key'))
        observation_list = owm.weather_around_coords(
            float(config.get('location', 'latitude')),
            float(config.get('location', 'longitude')),
        )
        observation = observation_list[0]
        self._location = observation.get_location()
        self._weather = observation.get_weather()

    def get_wind(self):
        """{'speed': 4.6, 'deg': 330}"""
        wind = self._weather.get_wind()
        return wind['speed']

    def get_temperature(self):
        """{'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}"""
        temperature = self._weather.get_temperature('celsius')
        return temperature['temp']
