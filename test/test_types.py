import unittest
from lively_lights.types import brightness, hue, saturation


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
