"""Gather informations about the environment lively lights is running in."""

import pyowm


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
