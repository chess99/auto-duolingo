import os

import uiautomator2 as u2

from tools.adb_utils import get_device_id


def get_app_hierarchy(device_id, output_path):
    # Connect to the device
    d = u2.connect(device_id)

    # Get the current UI hierarchy
    xml_hierarchy = d.dump_hierarchy()

    # Ensure the .temp directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Optionally, save the hierarchy to a file for inspection
    with open(output_path, "w") as file:
        file.write(xml_hierarchy)

    return xml_hierarchy


if __name__ == "__main__":
    device_id = get_device_id()
    if device_id is not None:
        get_app_hierarchy(device_id, ".temp/hierarchy.xml")
