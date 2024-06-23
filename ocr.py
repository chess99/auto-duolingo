from PIL import Image, ImageDraw, ImageFont
import pytesseract
from pytesseract import Output

def image_to_string(image_path):
    # Open the captured screenshot using PIL
    image = Image.open(image_path)

    # Use pytesseract to extract text from the image, specifying English, Simplified Chinese, and Japanese
    text = pytesseract.image_to_string(image, lang='eng+chi_sim+jpn')
    print(f"text: {text}")

    return text

def ocr_from_image(image_path):
    # Open the image
    image = Image.open(image_path)

    # Use pytesseract for OCR, specifying English, Simplified Chinese, and Japanese, and get the text position information
    data = pytesseract.image_to_string(image, lang='eng+chi_sim+jpn', output_type=Output.DICT)

    # Return the result
    return data


def ocr_from_image_with_position(image_path):
    # Open the image
    image = Image.open(image_path)

    # Use pytesseract to get OCR data, specifying languages and asking for detailed output
    data = pytesseract.image_to_data(image, lang='eng+chi_sim+jpn', output_type=Output.DICT)
    print(f"data: {data}")

    # Initialize an empty list to hold text with its position
    text_with_positions = []

    # Iterate over each item in the data to extract text and its bounding box
    for i in range(len(data['text'])):
        if data['text'][i].strip() != '':  # Ensure the text is not empty
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            text = data['text'][i]
            text_with_positions.append({'text': text, 'position': (x, y, w, h)})

    # Return the list of texts with their positions
    return text_with_positions


def mark_recognized_text_on_image(image_path, text_positions, output_path):
    # Open the original image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Optional: Load a font. Default fonts can be used or specify your own path
    try:
        # Attempt to load a font (you may need to adjust the path and size)
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        # If the specific font cannot be loaded, fall back to a default PIL font
        font = ImageFont.load_default()

    # Draw rectangles and text around recognized text
    for item in text_positions:
        position = item['position']
        text = item['text']
        # The position is a tuple (x, y, w, h)
        x, y, w, h = position
        draw.rectangle([x, y, x+w, y+h], outline="red")
        
        # Adjust text position if needed. Here, it's placed at the top-left corner of the rectangle
        text_position = (x, y - 10 if y - 10 > 0 else y + h)  # Ensure text is always visible
        draw.text(text_position, text, fill="blue", font=font)

    # Save the image to a new file
    image.save(output_path)


# Example usage
text_positions = ocr_from_image_with_position('.temp/big_image.png')
for item in text_positions:
    print(item)
mark_recognized_text_on_image('.temp/big_image.png', text_positions, '.temp/res2.png')