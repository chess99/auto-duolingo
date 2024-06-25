import time

from auto_duolingo.adb_utils import capture_screen, perform_click
from auto_duolingo.box import process_image_and_sort_text


def simulate_clicks_on_sorted_boxes(debug=False):
    # Step 1: Capture a screenshot and save it to the local .temp directory
    screenshot_filename = 'screenshot.png'
    local_save_path = '.temp'
    capture_screen(screenshot_filename, local_path=local_save_path)

    # Construct the full path to the screenshot
    screenshot_path = f"{local_save_path}/{screenshot_filename}"

    # Step 2: Process the image and get sorted boxes
    sorted_boxes = process_image_and_sort_text(screenshot_path)
    print(f"Sorted Boxes: {sorted_boxes}")

    # Step 3: Simulate clicks on the sorted boxes
    for _, (x, y, w, h) in sorted_boxes:
        # Calculate the center of the box to simulate the click
        click_x = x + w // 2
        click_y = y + h // 2

        perform_click(click_x, click_y)

        # Add a delay between clicks
        time.sleep(1)  # Adjust the delay as needed


if __name__ == "__main__":
    simulate_clicks_on_sorted_boxes()
