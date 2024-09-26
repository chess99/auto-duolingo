import cv2
import numpy as np


def enhance_contrast(image, alpha=1.5, beta=0):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def apply_threshold(image):
    _, thresh_image = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh_image


def erode_image(image, kernel_size=(1, 1), iterations=1):
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.erode(image, kernel, iterations=iterations)


def dilate_image(image, kernel_size=(1, 1), iterations=1):
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.dilate(image, kernel, iterations=iterations)


def preprocess_image_for_ocr(cropped_image: np.ndarray) -> np.ndarray:
    processing_steps = [
        enhance_contrast,
        to_gray,
        apply_threshold,
        # erode_image,
        # dilate_image
    ]

    cropped_image_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

    processed_image = cropped_image_rgb
    for step in processing_steps:
        processed_image = step(processed_image)

    return processed_image
