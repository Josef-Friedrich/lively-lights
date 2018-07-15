from lively_lights.environment import \
    DayNight, \
    host_up, \
    HostUp, \
    ReachableLights, \
    ReachableLightsFactory, \
    Weather
from _helper import mock_bridge, get_day_night
from freezegun import freeze_time
import os
import pwd
import unittest


INTERNET_CONNECTIFITY = host_up.is_up('8.8.8.8:53')

if 'TRAVIS' in os.environ:
    ON_TRAVIS = True
else:
    ON_TRAVIS = False


def get_username():
    return pwd.getpwuid(os.getuid()).pw_name


@unittest.skipIf(not INTERNET_CONNECTIFITY, 'No internet connectifity')
class TestClassHostUp(unittest.TestCase):

    def setUp(self):
        self.host_up = HostUp()
        self.host_up.timeout = 1

    @unittest.skipIf(ON_TRAVIS, 'ICMP not allowed on travis.')
    def test_method_ping_external_command_true(self):
        self.assertTrue(self.host_up._ping_external_command('8.8.8.8'))

    @unittest.skipIf(ON_TRAVIS, 'ICMP not allowed on travis.')
    def test_method_ping_external_command_false(self):
        self.assertFalse(self.host_up._ping_external_command('192.0.0.1'))

    @unittest.skipIf(get_username() != 'root', 'You have to be root')
    def test_method_ping_python_true(self):
        self.assertTrue(self.host_up._ping_python('8.8.8.8'))

    @unittest.skipIf(get_username() != 'root', 'You have to be root')
    def test_method_ping_python_false(self):
        self.assertFalse(self.host_up._ping_python('192.0.0.1'))

    def test_method_open_port_true(self):
        self.assertTrue(self.host_up._open_port('8.8.8.8', 53))

    def test_method_open_port_false(self):
        self.assertFalse(self.host_up._open_port('8.8.8.8', 52))

    def test_method_is_up_open_port_true(self):
        self.assertTrue(self.host_up.is_up('8.8.8.8:53'))

    def test_method_is_up_open_port_false(self):
        self.assertFalse(self.host_up.is_up('192.0.0.1:52'))

    @unittest.skipIf(ON_TRAVIS, 'ICMP not allowed on travis.')
    def test_method_is_up_ping_true(self):
        self.assertTrue(self.host_up.is_up('8.8.8.8'))

    @unittest.skipIf(ON_TRAVIS, 'ICMP not allowed on travis.')
    def test_method_is_up_ping_false(self):
        self.assertFalse(self.host_up.is_up('192.0.0.1'))


class TestClassDayNight(unittest.TestCase):

    def setUp(self):
        self.day_night = DayNight(
            49.455556,
            11.078611,
            'Europe/Berlin',
            309,
        )

    @freeze_time('2000-01-01 23:00:00')
    def test_is_night(self):
        self.assertTrue(self.day_night.is_night())

    @freeze_time('2000-01-01 12:00:00')
    def test_is_day(self):
        self.assertTrue(self.day_night.is_day())

    @freeze_time('2000-01-01 08:11:49+01')
    def test_is_night_close(self):
        self.assertTrue(self.day_night.is_night())

    @freeze_time('2000-01-01 08:11:50+01')
    def test_is_day_close(self):
        self.assertTrue(self.day_night.is_day())

    @freeze_time('2000-01-01 23:00:00')
    def test_overview(self):
        self.assertEqual(
            self.day_night.overview(),
            'Dawn:    2000-01-01 07:34:09+01:00\n'
            'Sunrise: 2000-01-01 08:11:49+01:00\n'
            'Noon:    2000-01-01 12:18:44+01:00\n'
            'Sunset:  2000-01-01 16:25:40+01:00\n'
            'Dusk:    2000-01-01 17:03:20+01:00'
        )


@unittest.skipIf(not INTERNET_CONNECTIFITY, 'No internet connectifity')
class TestClassWeather(unittest.TestCase):

    def setUp(self):

        self.weather = Weather(
            openweathermap_api_key='8a32360f1f4d8c729b64d344c53a0b92',
            latitude=49.455556,
            longitude=11.078611,
        )

    def test_init(self):
        self.assertTrue(self.weather)

    def test_method_get_wind(self):
        self.assertTrue(self.weather.get_wind())

    def test_method_get_temperature(self):
        self.assertTrue(self.weather.get_temperature())

    def test_location(self):
        self.assertEqual(self.weather._location.get_name(), 'Nuremberg')


class TestClassReachableLights(unittest.TestCase):

    def get_reachable_lights(self, *light_configs, **kwargs):
        return ReachableLights(mock_bridge(light_configs), get_day_night(),
                               **kwargs)

    def test_method_list(self):
        lights = self.get_reachable_lights([1, True], [2, True])
        self.assertEqual(lights.get_light_ids(), [1, 2])
        self.assertTrue(lights._lights_refresh_state[1][1])
        self.assertTrue(lights._lights_refresh_state[2][1])

    def test_iterator_all_reachable(self):
        lights = self.get_reachable_lights([1, True], [2, True])
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [1, 2])

    def test_iterator_all_unreachable(self):
        lights = self.get_reachable_lights([1, False], [2, False])
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [])

    def test_iterator_last_reachable(self):
        lights = self.get_reachable_lights([3, False], [2, True])
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [2])

    def test_parameter_light_ids(self):
        lights = self.get_reachable_lights([1, True], [2, True], light_ids=[1])
        self.assertEqual(lights.get_light_ids(), [1])

    @freeze_time('2000-01-01 23:00:00')
    def test_parameter_not_at_night_true_by_night(self):
        lights = self.get_reachable_lights([1, True], not_at_night=True)
        self.assertEqual(lights.get_light_ids(), [])

    @freeze_time('2000-01-01 23:00:00')
    def test_parameter_not_at_night_false_by_night(self):
        lights = self.get_reachable_lights([1, True], not_at_night=False)
        self.assertEqual(lights.get_light_ids(), [1])

    @freeze_time('2000-01-01 12:00:00')
    def test_parameter_not_at_night_true_by_day(self):
        lights = self.get_reachable_lights([1, True], not_at_night=True)
        self.assertEqual(lights.get_light_ids(), [1])

    @freeze_time('2000-01-01 12:00:00')
    def test_parameter_not_at_night_false_by_day(self):
        lights = self.get_reachable_lights([1, True], not_at_night=False)
        self.assertEqual(lights.get_light_ids(), [1])
        self.assertTrue(lights._bridge[1].on)

    @freeze_time('2000-01-01 12:00:00')
    def test_parameter_turn_off(self):
        lights = self.get_reachable_lights([1, True], not_during_daytime=True,
                                           turn_off=True)
        self.assertEqual(lights.get_light_ids(), [])
        self.assertEqual(lights._bridge[1].on, False)
        self.assertTrue(lights._lights_turn_off_state[1])


class TestClassReachableLightsFactory(unittest.TestCase):

    def setUp(self):
        self.factory = ReachableLightsFactory(mock_bridge([[1, True]]),
                                              get_day_night())

    def test_init(self):
        self.assertTrue(self.factory._bridge)
        self.assertTrue(self.factory._day_night)
        self.assertEqual(self.factory._refresh_interval, 60)

    def test_get_lights(self):
        reachable_lights = self.factory.get_lights(1)
        self.assertTrue(reachable_lights)
        self.assertEqual(reachable_lights.__class__.__name__,
                         'ReachableLights')
