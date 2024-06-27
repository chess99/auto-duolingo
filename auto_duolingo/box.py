from typing import List, Tuple

import cv2
import numpy as np

from auto_duolingo.ocr_tesseract import ocr_on_single_box_tesseract
from auto_duolingo.translate_llm import generate_sorted_sentence


def detect_boxes_in_image(image_path: str) -> List[Tuple[int, int, int, int]]:
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    # Apply morphological gradient to help highlight the edges
    kernel = np.ones((5, 5), np.uint8)
    gradient = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel)

    # Find contours
    contours, _ = cv2.findContours(
        gradient, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []  # Initialize an empty list to store bounding boxes
    for cnt in contours:
        # Approximate the contour to a polygon
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # Check if the approximated contour is a rectangle
        if cv2.contourArea(cnt) > 10000 and cv2.isContourConvex(approx):
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h
            # Filter based on aspect ratio to ensure we're targeting rectangular shapes
            if 0.5 < aspect_ratio < 10:  # Adjust these values based on the expected box aspect ratio
                boxes.append((x, y, w, h))  # Append bounding box to the list

    return boxes  # Return the list of bounding boxes


# def ocr_on_boxes(image_path: str, boxes: List[Tuple[int, int, int, int]]) -> List[Tuple[str, Tuple[int, int, int, int]]]:
#     image = cv2.imread(image_path)
#     results = []

#     for i, box in enumerate(boxes[2:], start=2):  # Start from the third box
#         lang = 'ch_sim' if i == len(boxes) - 1 else 'ja'
#         x, y, w, h = box
#         cropped_image = image[y:y+h, x:x+w]
#         text_strip = ocr_on_single_box(cropped_image, lang)
#         results.append((text_strip, box))

#     return results


def ocr_on_boxes(image_path: str, boxes: List[Tuple[int, int, int, int]]) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    image = cv2.imread(image_path)
    results = []

    for i, box in enumerate(boxes[2:], start=2):  # Start from the third box
        is_last_box = i == len(boxes) - 1
        lang = 'chi_sim' if is_last_box else 'jpn'
        custom_config = r'--oem 3 --psm 3' if is_last_box else r'--oem 3 --psm 6'
        x, y, w, h = box
        cropped_image = image[y:y+h, x:x+w]
        text_strip = ocr_on_single_box_tesseract(
            cropped_image, lang, custom_config)
        results.append((text_strip, box))

    return results


def process_image_and_sort_text(image_path: str) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    # Detect text boxes in the image
    text_boxes = detect_boxes_in_image(image_path)

    # Extract text and positions from the detected boxes
    extracted_text_boxes = ocr_on_boxes(image_path, text_boxes)

    # Isolate the sentence for sorting and the associated word positions
    # Assuming the last box contains the sentence
    sentence_for_sorting = extracted_text_boxes[-1][0]
    word_positions = extracted_text_boxes[:-1]  # Exclude the sentence box

    # Separate words for sorting process
    words_to_sort = [word for word, _ in word_positions]

    # Sort words based on the original sentence
    sorted_word_list = generate_sorted_sentence(
        sentence_for_sorting, words_to_sort)

    # Associate sorted words with their original positions
    word_position_mapping = {
        word: position for word, position in word_positions}
    sorted_text_boxes = [(word, word_position_mapping[word])
                         for word in sorted_word_list if word in word_position_mapping]

    return sorted_text_boxes


# Example usage
if __name__ == "__main__":
    image_path = "demo_images/chi_jpn_2.jpg"
    boxes = process_image_and_sort_text(image_path)
    print(boxes)
