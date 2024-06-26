
import sys

from auto_duolingo.DuolingoBot import DuolingoBot
from tools.adb_utils import get_device_id

if __name__ == "__main__":
    device_id = get_device_id()
    if device_id is None:
        sys.exit(1)
    bot = DuolingoBot(device_id)
    bot.run()
