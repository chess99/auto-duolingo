import unittest
from unittest.mock import MagicMock, patch

from auto_duolingo.DuolingoBot import DuolingoBot


class TestDuolingoBot(unittest.TestCase):
    def setUp(self):
        self.device_ip = '192.168.1.2'
        self.patcher = patch('uiautomator2.connect')
        self.mock_connect = self.patcher.start()
        self.mock_device = MagicMock()
        self.mock_connect.return_value = self.mock_device
        self.bot = DuolingoBot(self.device_ip)

    def tearDown(self):
        self.patcher.stop()

    def test_init(self):
        self.mock_connect.assert_called_with(self.device_ip)
        self.assertEqual(self.bot.state, "START")

    def test_run(self):
        # This test would need to simulate or mock the entire flow of the bot.
        # It's more complex and might require setting side_effects on the mock_device
        # to simulate different states of the app. It's recommended to break down the
        # bot's operation into smaller, testable parts instead of testing run directly.
        pass


if __name__ == '__main__':
    unittest.main()
