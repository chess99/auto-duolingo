import cv2


def match_image(big_image_path, small_image_path, threshold):
    img_rgb = cv2.imread(big_image_path)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(small_image_path, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        return img_rgb, top_left, bottom_right
    else:
        return None, None, None


def draw_and_save(img_rgb, top_left, bottom_right, output_path):
    if img_rgb is not None and top_left is not None and bottom_right is not None:
        cv2.rectangle(img_rgb, top_left, bottom_right, (0, 0, 255), 2)
        cv2.imwrite(output_path, img_rgb)


# Adjust the paths to include the .temp/ directory
big_image_path = '.temp/big_image.png'
small_image_path = '.temp/small_image.png'
output_path = '.temp/res.png'

img_rgb, top_left, bottom_right = match_image(
    big_image_path, small_image_path, 0.8)
draw_and_save(img_rgb, top_left, bottom_right, output_path)

if top_left is not None:
    print("Match found at", top_left)
else:
    print("No match found")
