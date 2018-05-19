import unittest
from lively_lights.types import _range, \
                                brightness, \
                                hue, \
                                light_id, \
                                time, \
                                transition_time, \
                                saturation


class TestRange(unittest.TestCase):

    def test_list(self):
        self.assertEqual(_range([1, 2], hue), (1, 2))

    def test_tuple(self):
        self.assertEqual(_range((1, 2), hue), (1, 2))

    def test_less(self):
        with self.assertRaises(ValueError):
            _range((1, ), hue)

    def test_more(self):
        with self.assertRaises(ValueError):
            _range((1, 2, 3), hue)

    def test_max_less_than_min(self):
        with self.assertRaises(ValueError):
            _range((2, 1), hue)

    def test_wrong_inner_type(self):
        with self.assertRaises(ValueError):
            _range(('lol', 2), hue)


class TestBrightness(unittest.TestCase):

    def test_valid_min(self):
        self.assertEqual(brightness(1), 1)

    def test_valid_normal(self):
        self.assertEqual(brightness(100), 100)

    def test_valid_max(self):
        self.assertEqual(brightness(254), 254)

    def test_valid_min_string(self):
        self.assertEqual(brightness('1'), 1)

    def test_valid_max_string(self):
        self.assertEqual(brightness('254'), 254)

    def test_valid_float(self):
        self.assertEqual(brightness(2.3), 2)

    def test_valid_float_cut(self):
        self.assertEqual(brightness(2.9), 2)

    def test_invalid_min(self):
        with self.assertRaises(ValueError):
            brightness(0)

    def test_invalid_max(self):
        with self.assertRaises(ValueError):
            brightness(255)

    def test_invalid_negativ(self):
        with self.assertRaises(ValueError):
            brightness(-1)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            brightness('lol')


class TestHue(unittest.TestCase):

    def test_valid_min(self):
        self.assertEqual(hue(0), 0)

    def test_valid_normal(self):
        self.assertEqual(hue(100), 100)

    def test_valid_max(self):
        self.assertEqual(hue(65535), 65535)

    def test_valid_min_string(self):
        self.assertEqual(hue('0'), 0)

    def test_valid_max_string(self):
        self.assertEqual(hue('65535'), 65535)

    def test_valid_float(self):
        self.assertEqual(hue(2.3), 2)

    def test_valid_float_cut(self):
        self.assertEqual(hue(2.9), 2)

    def test_invalid_min(self):
        with self.assertRaises(ValueError):
            hue(-1)

    def test_invalid_max(self):
        with self.assertRaises(ValueError):
            hue(65536)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            hue('lol')


class TestLightId(unittest.TestCase):

    def test_valid_min(self):
        self.assertEqual(light_id(1), 1)

    def test_valid_normal(self):
        self.assertEqual(light_id(100), 100)

    def test_valid_min_string(self):
        self.assertEqual(light_id('1'), 1)

    def test_valid_float(self):
        self.assertEqual(light_id(2.3), 2)

    def test_valid_float_cut(self):
        self.assertEqual(light_id(2.9), 2)

    def test_invalid_min(self):
        with self.assertRaises(ValueError):
            light_id(0)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            light_id('lol')


class TestTime(unittest.TestCase):

    def test_valid_min(self):
        self.assertEqual(time(0), 0)

    def test_valid_normal(self):
        self.assertEqual(time(10), 10)

    def test_valid_min_string(self):
        self.assertEqual(time('0'), 0)

    def test_valid_float(self):
        self.assertEqual(time(2.3), 2.3)

    def test_invalid_min(self):
        with self.assertRaises(ValueError):
            time(-1)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            time('lol')


class TesttTransitionTime(unittest.TestCase):

    def test_valid_min(self):
        self.assertEqual(transition_time(0), 0)

    def test_valid_normal(self):
        self.assertEqual(transition_time(10), 100)

    def test_valid_max(self):
        self.assertEqual(transition_time(6553.5), 65535)

    def test_valid_min_string(self):
        self.assertEqual(transition_time('0'), 0)

    def test_valid_max_string(self):
        self.assertEqual(transition_time('6553.5'), 65535)

    def test_valid_float(self):
        self.assertEqual(transition_time(2.3), 23)

    def test_valid_float_cut(self):
        self.assertEqual(transition_time(2.9), 29)

    def test_invalid_min(self):
        with self.assertRaises(ValueError):
            transition_time(-1)

    def test_invalid_max(self):
        with self.assertRaises(ValueError):
            transition_time(6553.6)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            transition_time('lol')


class TestSaturation(unittest.TestCase):

    def test_valid_min(self):
        self.assertEqual(saturation(0), 0)

    def test_valid_normal(self):
        self.assertEqual(saturation(100), 100)

    def test_valid_max(self):
        self.assertEqual(saturation(254), 254)

    def test_valid_min_string(self):
        self.assertEqual(saturation('0'), 0)

    def test_valid_max_string(self):
        self.assertEqual(saturation('254'), 254)

    def test_valid_float(self):
        self.assertEqual(saturation(2.3), 2)

    def test_valid_float_cut(self):
        self.assertEqual(saturation(2.9), 2)

    def test_invalid_min(self):
        with self.assertRaises(ValueError):
            saturation(-1)

    def test_invalid_max(self):
        with self.assertRaises(ValueError):
            saturation(255)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            saturation('lol')
