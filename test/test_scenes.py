from _helper import get_reachable_lights
from lively_lights import scenes, types
from lively_lights.scenes import Launcher, \
                                 Scene, \
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

    properties = {
        'speed': {
            'type': types.time,
        },
        'color': {
            'type': types.hue,
        },
    }


class TestClassScene(unittest.TestCase):

    def test_kwargs_error(self):
        with self.assertRaises(ValueError):
            Scene('', '', arg1=1)

    def test_kwargs(self):
        scene = SceneTest('', '', speed=1, color=2)
        self.assertEqual(scene.speed, 1)
        self.assertEqual(scene.color, 2)

    def test_method_get_properties_from_args(self):
        scene = SceneTest('', '', speed=1, color=2)
        args = Args()
        scene.get_properties_from_args(args)
        self.assertEqual(scene.speed, 111)
        self.assertEqual(scene.color, 222)

    def test_method_get_properties_from_dict(self):
        scene = SceneTest('', '', speed=1, color=2)
        dictionary = {
            'speed': 111
        }
        scene.get_properties_from_dict(dictionary)
        self.assertEqual(scene.speed, 111)


class TestClassSceneBreath(unittest.TestCase):

    def test_kwargs(self):
        scene = SceneBreath('', '', brightness_range=(1, 2), hue_range=(3, 4),
                            time_range=(5, 6))
        self.assertEqual(scene.brightness_range, (1, 2))
        self.assertEqual(scene.hue_range, (3, 4))
        self.assertEqual(scene.time_range, (5, 6))

    def test_set_defaults(self):
        scene = SceneBreath('', '')
        scene._set_defaults()
        self.assertTrue(scene.brightness_range)
        self.assertTrue(scene.hue_range)
        self.assertTrue(scene.time_range)


class TestClassScenePendulum(unittest.TestCase):

    def test_kwargs(self):
        scene = ScenePendulum('', '', color1=1, color2=2, lights1=(3, ),
                              lights2=(4, ), sleep_time=5, transition_time=6)
        self.assertEqual(scene.color1, 1)
        self.assertEqual(scene.color2, 2)
        self.assertEqual(scene.lights1, [3])
        self.assertEqual(scene.lights2, [4])
        self.assertEqual(scene.sleep_time, 5)
        self.assertEqual(scene.transition_time, 6)

    def test_set_defaults(self):
        scene = ScenePendulum('', '', lights1=(1, ), lights2=(2, ))
        scene._set_defaults()
        self.assertTrue(scene.color1)
        self.assertTrue(scene.color2)
        self.assertTrue(scene.lights1)
        self.assertTrue(scene.lights2)
        self.assertTrue(scene.sleep_time)
        self.assertTrue(scene.transition_time)


class TestClassSceneSequence(unittest.TestCase):

    def test_kwargs(self):
        scene = SceneSequence('', '', brightness=1, hue_sequence=(2, ),
                              sleep_time=3, transition_time=4)
        self.assertEqual(scene.brightness, 1)
        self.assertEqual(scene.hue_sequence, [2])
        self.assertEqual(scene.sleep_time, 3)
        self.assertEqual(scene.transition_time, 4)

    def test_set_defaults(self):
        scene = SceneSequence('', '')
        scene._set_defaults()
        self.assertTrue(scene.brightness)
        self.assertTrue(scene.hue_sequence)
        self.assertTrue(scene.sleep_time)
        self.assertTrue(scene.transition_time)

    @mock.patch('lively_lights.scenes.set_light_multiple')
    def test_start(self, set_light_multiple):
        reachable_lights = mock.Mock()
        reachable_lights.list.return_value = [mock.Mock()]
        scene = SceneSequence(
            mock.Mock(),
            reachable_lights,
            brightness=100,
            hue_sequence=(1, 100),
            sleep_time=1,
            transition_time=2,
        )
        scene.start(5)
        call_list = set_light_multiple.call_args_list

        self.assertEqual(call_list[0][0][2]['hue'], 1)
        self.assertEqual(call_list[1][0][2]['hue'], 100)
        self.assertEqual(call_list[2][0][2]['hue'], 1)

        self.assertEqual(call_list[0][0][2]['bri'], 100)
        self.assertEqual(call_list[0][0][2]['transitiontime'], 20)


class TestClassSceneTimeOuts(unittest.TestCase):

    @mock.patch('lively_lights.scenes.set_light_multiple', mock.Mock())
    def assertTimeOut(self, scene, time_out):
        get_reachable_lights([1, 2])
        reachable_lights = get_reachable_lights([1, 2])
        Scene = getattr(scenes, scene)
        scene = Scene(mock.Mock(), reachable_lights)
        begin = time.time()
        scene.start(time_out)
        end = time.time()
        self.assertTrue(scene.time_out)
        self.assertTrue(scene.actual_duration)
        self.assertTrue(end - begin <= time_out,
                        'time_out not longer (Scene: {})'. format(scene))
        # self.assertTrue(end - begin >= time_out - 3,
        #                 'time_out not shorter (Scene: {})'. format(scene))

    def test_scene_pendulum(self):
        self.assertTimeOut('ScenePendulum', 10)

    def test_scene_sequence(self):
        self.assertTimeOut('SceneSequence', 10)


class TestClassLauncher(unittest.TestCase):

    def test_method_get_scene_class(self):
        scene = Launcher._get_scene_class('pendulum')
        self.assertEqual(scene.__name__, 'ScenePendulum')

    def test_method_get_scene_class_exception(self):
        with self.assertRaises(AttributeError):
            Launcher._get_scene_class('xxx')

    def test_method_launch_scene(self):
        scene_config = {
            'title': 'Rainbow',
            'description': 'Cycle between three colors',
            'scene_name': 'sequence',
            'duration': 3,
            'properties': {
                'brightness': 254,
                'hue_sequence': [0, 40000, 30000],
                'sleep_time': 2,
                'transition_time': 1,
            },
        }
        launcher = Launcher(mock.Mock(), get_reachable_lights([1, 2]))
        launcher.launch_scene(scene_config)
