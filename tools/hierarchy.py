import os
import time  # Import the time module at the beginning of the file

import uiautomator2 as u2

from tools.adb_utils import get_device_id


def get_app_hierarchy(device_id, output_path):
    start_time = time.time()  # Capture start time
    print(f"Getting UI hierarchy for device {device_id}...")

    d = u2.connect(device_id)
    xml_hierarchy = d.dump_hierarchy()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as file:
        file.write(xml_hierarchy)

    end_time = time.time()  # Capture end time
    print(f"Time taken: {end_time - start_time} seconds")  # Print the time taken

    return xml_hierarchy


if __name__ == "__main__":
    device_id = get_device_id()
    if device_id is not None:
        get_app_hierarchy(device_id, ".temp/hierarchy.xml")
