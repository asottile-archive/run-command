import unittest

from run_command import run_command
from run_command import NORMAL
from run_command import ERROR
from run_command import KILLED_TIME
from run_command import KILLED_LENGTH

class TestRunProcess(unittest.TestCase):
    def test_command_that_finishes(self):
        reason, code, output = run_command(
            ['echo', 'hello world']
        )
        self.assertEqual(reason, NORMAL)
        self.assertEqual(code, 0)
        self.assertEqual(output, 'hello world\n')

    def test_command_too_much_length(self):
        reason, code, output = run_command(
            ['yes'],
            max_length=100
        )
        self.assertEqual(reason, KILLED_LENGTH)
        self.assertNotEqual(code, 0)
        assert len(output) <= 100

    def test_command_too_much_time(self):
        reason, code, output = run_command(
            ['sleep', '5'],
            timeout=1,
        )
        self.assertEqual(reason, KILLED_TIME)
        self.assertNotEqual(code, 0)

    def test_command_that_doesnt_exist(self):
        reason, code, output = run_command(['./herp'])
        self.assertEqual(reason, ERROR)
        self.assertNotEqual(code, 0)
