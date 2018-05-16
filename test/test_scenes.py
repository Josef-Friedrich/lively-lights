from lively_lights.scenes import Scene
import unittest


class Args(object):

    speed = 111
    color = 222


class SceneTest(Scene):

    properties = ['speed', 'color']


class TestClassScene(unittest.TestCase):

    def test_kwargs(self):
        with self.assertRaises(ValueError):
            Scene('lol', 'lol', arg1=1)


class TestClassSceneInheritage(unittest.TestCase):

    def test_kwargs(self):
        scene = SceneTest('lol', 'lol', speed=1, color=2)
        self.assertEqual(scene.speed, 1)
        self.assertEqual(scene.color, 2)

    def test_method_get_properties_from_args(self):
        scene = SceneTest('lol', 'lol')
        args = Args()
        scene.get_properties_from_args(args)
        self.assertEqual(scene.speed, 111)
        self.assertEqual(scene.color, 222)
