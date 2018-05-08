import subprocess
import unittest

comamnd_name = 'lively-lights.py'
usage = 'usage: {}'.format(comamnd_name)


class TestCli(unittest.TestCase):

    def test_without_arguments(self):

        run = subprocess.run([comamnd_name], encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue(usage in run.stderr)

    def test_help(self):
        run = subprocess.run([comamnd_name, '-h'], encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(run.returncode, 0)
        self.assertTrue(usage in run.stdout)
