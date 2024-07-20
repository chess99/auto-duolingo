import unittest
from unittest.mock import MagicMock, patch

from auto_duolingo.ui_helper.DuolingoUIHelper import DuolingoUIHelper


class TestDuolingoUIHelper(unittest.TestCase):
    def setUp(self):
        patcher1 = patch(
            'tools.adb_utils.get_device_id', return_value='dummy_device_id')
        self.mock_get_device_id = patcher1.start()
        self.addCleanup(patcher1.stop)

        patcher2 = patch(
            'uiautomator2.connect', return_value=MagicMock())
        self.mock_u2_connect = patcher2.start()
        self.addCleanup(patcher2.stop)

        self.helper = DuolingoUIHelper()


if __name__ == '__main__':
    unittest.main()
