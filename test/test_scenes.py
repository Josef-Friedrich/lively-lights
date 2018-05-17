from lively_lights import scenes
from lively_lights.scenes import Scene, \
                                 SceneBreath, \
                                 ScenePendulum, \
                                 SceneSequence
import unittest
from unittest import mock
import time


class Args(object):

    speed = 111
    color = 222


class SceneTest(Scene):

    properties = ['speed', 'color']


class TestClassScene(unittest.TestCase):

    def test_kwargs(self):
        with self.assertRaises(ValueError):
            Scene('', '', arg1=1)

    def test_method_get_properties_from_args(self):
        scene = Scene('', '')
        scene.properties = ['speed', 'arg2']
        args = Args()
        scene.get_properties_from_args(args)
        self.assertEqual(scene.speed, 111)


class TestClassSceneInheritage(unittest.TestCase):

    def test_kwargs(self):
        scene = SceneTest('', '', speed=1, color=2)
        self.assertEqual(scene.speed, 1)
        self.assertEqual(scene.color, 2)

    def test_method_get_properties_from_args(self):
        scene = SceneTest('', '')
        args = Args()
        scene.get_properties_from_args(args)
        self.assertEqual(scene.speed, 111)
        self.assertEqual(scene.color, 222)


class TestClassSceneBreath(unittest.TestCase):

    def test_kwargs(self):
        scene = SceneBreath('', '', bri_range=1, hue_range=2, time_range=3)
        self.assertEqual(scene.bri_range, 1)
        self.assertEqual(scene.hue_range, 2)
        self.assertEqual(scene.time_range, 3)

    def test_setup(self):
        scene = SceneBreath('', '')
        scene._setup()
        self.assertTrue(scene.bri_range)
        self.assertTrue(scene.hue_range)
        self.assertTrue(scene.time_range)


class TestClassScenePendulum(unittest.TestCase):

    def test_kwargs(self):
        scene = ScenePendulum('', '', color_1=1, color_2=2, lights_1=3,
                              lights_2=4, sleep_time=5, transition_time=6)
        self.assertEqual(scene.color_1, 1)
        self.assertEqual(scene.color_2, 2)
        self.assertEqual(scene.lights_1, 3)
        self.assertEqual(scene.lights_2, 4)
        self.assertEqual(scene.sleep_time, 5)
        self.assertEqual(scene.transition_time, 6)

    def test_setup(self):
        scene = ScenePendulum('', '', lights_1=1, lights_2=2)
        scene._setup()
        self.assertTrue(scene.color_1)
        self.assertTrue(scene.color_2)
        self.assertTrue(scene.lights_1)
        self.assertTrue(scene.lights_2)
        self.assertTrue(scene.sleep_time)
        self.assertTrue(scene.transition_time)


class TestClassSceneSequence(unittest.TestCase):

    def test_kwargs(self):
        scene = SceneSequence('', '', brightness=1, hue_sequence=2,
                              sleep_time=3, transition_time=4)
        self.assertEqual(scene.brightness, 1)
        self.assertEqual(scene.hue_sequence, 2)
        self.assertEqual(scene.sleep_time, 3)
        self.assertEqual(scene.transition_time, 4)

    def test_setup(self):
        scene = SceneSequence('', '')
        scene._setup()
        self.assertTrue(scene.brightness)
        self.assertTrue(scene.hue_sequence)
        self.assertTrue(scene.sleep_time)
        self.assertTrue(scene.transition_time)


class TestClassSceneTimeOuts(unittest.TestCase):

    @mock.patch('lively_lights.scenes.set_light_multiple', mock.Mock())
    def assertTimeOut(self, scene, time_out):
        reachable_lights = mock.Mock()
        reachable_lights.list.return_value = [mock.Mock(), mock.Mock()]
        Scene = getattr(scenes, scene)
        scene = Scene(mock.Mock(), reachable_lights)
        begin = time.time()
        scene.start(time_out)
        end = time.time()
        self.assertTrue(end - begin <= time_out,
                        'time_out not longer (Scene: {})'. format(scene))
        # self.assertTrue(end - begin >= time_out - 3,
        #                 'time_out not shorter (Scene: {})'. format(scene))

    def test_scene_pendulum(self):
        self.assertTimeOut('ScenePendulum', 10)

    def test_scene_sequence(self):
        self.assertTimeOut('SceneSequence', 10)
