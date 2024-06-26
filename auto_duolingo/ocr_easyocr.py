"""
API Documentation: https://www.jaided.ai/easyocr/
"""

import easyocr

from auto_duolingo.ocr_preprocess import preprocess_image_for_ocr


def ocr_on_single_box(cropped_image, lang='ja') -> str:
    processed_image = preprocess_image_for_ocr(cropped_image)
    reader = easyocr.Reader([lang], gpu=True)
    results = reader.readtext(
        processed_image)
    print(f"results: {results}")

    # Concatenate all detected text segments
    text = ''.join([result[1] for result in results])

    return text
