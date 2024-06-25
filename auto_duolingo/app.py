"""
Module for processing an app and capturing its screen.
This module contains functions to check if an app has launched,
wait for a specified amount of time, and then capture the screen.
"""

import time

from auto_duolingo.adb_utils import capture_screen, check_app_launched


def process_app_and_capture_screen(app_name, wait_time=5):
    """
    Launches the specified app and captures its screen after a delay.

    Args:
        app_name: The package name of the app to be processed.
        wait_time: The time in seconds to wait before capturing the screen. Defaults to 5 seconds.
    """
    check_app_launched(app_name)
    # Wait for the app to fully launch
    time.sleep(wait_time)
    capture_screen(local_path='.temp')


process_app_and_capture_screen('com.duolingo')
