from adb_utils import check_app_launched,capture_screen
import time

def process_app_and_capture_screen(app_name, wait_time=5):
    check_app_launched(app_name)
    # Wait for the app to fully launch
    time.sleep(wait_time)
    capture_screen(path='.temp')
    
process_app_and_capture_screen('com.duolingo')