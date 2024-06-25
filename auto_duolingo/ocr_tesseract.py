import pytesseract
from PIL import Image

from auto_duolingo.ocr_preprocess import preprocess_image_for_ocr


def ocr_on_single_box_tesseract(cropped_image, lang='jpn', custom_config=r'--oem 3 --psm 3') -> str:
    processed_image = preprocess_image_for_ocr(cropped_image)

    text = pytesseract.image_to_string(Image.fromarray(
        processed_image), lang=lang, config=custom_config)

    text_strip = "".join(text.split())

    print(f"text_strip: {text_strip}")
    return text_strip
