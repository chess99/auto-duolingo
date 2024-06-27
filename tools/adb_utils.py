import os
import subprocess


def list_devices():
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8').splitlines()
    devices = [line.split('\t')[0] for line in lines if '\tdevice' in line]
    print(f"Found {len(devices)} devices: {devices}")
    return devices


def select_device(devices):
    if len(devices) == 1:
        return devices[0]
    else:
        for i, device in enumerate(devices):
            print(f"{i + 1}. {device}")
        choice = int(input("Select a device by entering its number: ")) - 1
        return devices[choice]


def get_device_id():
    devices = list_devices()
    if not devices:
        print("No devices found.")
        return None
    device_id = select_device(devices)
    return device_id


def check_app_launched(package_name):
    # Get the list of currently running apps
    output = os.popen(
        'adb shell "dumpsys activity activities | grep -i ' + package_name + '"').read()

    # Check if the package name is in the list of running apps
    if package_name in output:
        print("App is already running")
    else:
        print("App is not running, launching it now...")
        os.system('adb shell monkey -p ' + package_name +
                  ' -c android.intent.category.LAUNCHER 1')


def check_current_app():
    # Get the output of the 'dumpsys window windows' command
    output = os.popen('adb shell "dumpsys window windows"').read()

    # Print the output for debugging
    print(output)

    # Find the line containing the currently focused app
    line = next((line for line in output.splitlines()
                if 'mFocusedApp' in line), None)
    if line is not None:
        # Extract the package name from the line
        package_name = line.split()[3].split('/')[0]
        return package_name
    else:
        print("No focused app found")
        return None


def capture_screen(filename='screenshot.png', local_path='.'):
    # Ensure the directory exists
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # Use adb command to capture the screen and save it as a file
    command = f'adb shell screencap -p /sdcard/{filename}'
    os.system(command)

    # Pull the file from the device to the specified full local path
    command = f'adb pull /sdcard/{filename} {local_path}/{filename}'
    os.system(command)

    # Remove the file from the device
    command = f'adb shell rm /sdcard/{filename}'
    os.system(command)


def remove_local_file(filename, local_path='.'):
    file_path = os.path.join(local_path, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


def perform_click(x, y):
    command = f'adb shell input tap {x} {y}'
    os.system(command)
