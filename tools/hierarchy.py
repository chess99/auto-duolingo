import os

import uiautomator2 as u2


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


# Example usage
device_id = "172.18.229.168:5555"
hierarchy = get_app_hierarchy(device_id, ".temp/ui_hierarchy.xml")
print(hierarchy)
