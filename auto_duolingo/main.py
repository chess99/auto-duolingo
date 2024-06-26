
import subprocess
import sys

from auto_duolingo.DuolingoBot import DuolingoBot


def list_devices():
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8').splitlines()
    devices = [line.split('\t')[0] for line in lines if '\tdevice' in line]
    return devices


def select_device(devices):
    if len(devices) == 1:
        return devices[0]
    else:
        for i, device in enumerate(devices):
            print(f"{i + 1}. {device}")
        choice = int(input("Select a device by entering its number: ")) - 1
        return devices[choice]


if __name__ == "__main__":
    devices = list_devices()
    if not devices:
        print("No devices found.")
        sys.exit(1)
    device_id = select_device(devices)
    bot = DuolingoBot(device_id)
    bot.run()
