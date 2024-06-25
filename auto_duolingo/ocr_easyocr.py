

import cv2
import easyocr
import numpy as np


def preprocess_image_for_ocr(cropped_image: np.ndarray) -> np.ndarray:
    # Convert the image to RGB (for pytesseract compatibility)
    cropped_image_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

    # Image preprocessing: enhance contrast
    alpha = 1.5  # Contrast control (1.0-3.0)
    beta = 0  # Brightness control (0-100)
    adjusted = cv2.convertScaleAbs(cropped_image_rgb, alpha=alpha, beta=beta)

    # Convert to grayscale for thresholding
    gray_image = cv2.cvtColor(adjusted, cv2.COLOR_RGB2GRAY)

    # Apply thresholding
    _, thresh_image = cv2.threshold(
        gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Erosion to make the text lines thinner and reduce noise
    # You can adjust the kernel size as needed
    kernel = np.ones((1, 1), np.uint8)
    eroded_image = cv2.erode(thresh_image, kernel, iterations=1)

    return eroded_image


def ocr_on_single_box(cropped_image, lang='ja') -> str:
    processed_image = preprocess_image_for_ocr(cropped_image)
    reader = easyocr.Reader([lang], gpu=True)
    results = reader.readtext(processed_image)
    print(f"results: {results}")

    # Concatenate all detected text segments
    text = ''.join([result[1] for result in results])

    return text
