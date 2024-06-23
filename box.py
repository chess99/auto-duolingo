import cv2
import numpy as np
import pytesseract
from PIL import Image
from langdetect import detect
from typing import List, Tuple
from order import generate_sorted_sentence

# ========== Helper functions ==========

def display_image(window_name, image):
    # Resize image for display if it's too large
    max_height = 600
    max_width = 800
    height, width = image.shape[:2]
    scaling_factor = min(max_width/width, max_height/height)
    if scaling_factor < 1:
        image = cv2.resize(image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

def display_detected_boxes(image_path, boxes):
    # Load the image
    image = cv2.imread(image_path)
    
    # Draw each box on the image and mark the index
    for index, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # Position for the index text: slightly above and to the left of the box
        text_position = (x, y - 10 if y - 10 > 10 else y + 20)
        # Put the index number on the box with a larger font size
        cv2.putText(image, str(index), text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Display the image with boxes
    display_image("Detected Boxes", image)
    
# ========== Main functions ==========

def detect_boxes_in_image(image_path: str) -> List[Tuple[int, int, int, int]]:
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)

    # Apply morphological gradient to help highlight the edges
    kernel = np.ones((5,5), np.uint8)
    gradient = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel)

    # Find contours
    contours, _ = cv2.findContours(gradient, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
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

def ocr_on_boxes(image_path: str, boxes: List[Tuple[int, int, int, int]]) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    image = cv2.imread(image_path)
    results = []  # Initialize an empty list to store OCR results with coordinates
    num_boxes = len(boxes)

    for i, (x, y, w, h) in enumerate(boxes):
        if i < 2:  # Skip the first two boxes
            continue
        # Crop the image to the box
        cropped_image = image[y:y+h, x:x+w]
        # Convert the image to RGB (for pytesseract compatibility)
        cropped_image_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        
        # Image preprocessing: enhance contrast
        alpha = 1.5  # Contrast control (1.0-3.0)
        beta = 0  # Brightness control (0-100)
        adjusted = cv2.convertScaleAbs(cropped_image_rgb, alpha=alpha, beta=beta)
        
        # Apply thresholding to filter out noise and improve OCR accuracy
        # Convert to grayscale for thresholding
        gray_image = cv2.cvtColor(adjusted, cv2.COLOR_RGB2GRAY)
        # Apply thresholding
        _, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Determine the language for OCR and set the appropriate PSM value
        if i == num_boxes - 1:  # If it's the last box, use Chinese and PSM 6
            lang = 'chi_sim'
            custom_config = r'--oem 3 --psm 3'
        else:  # For other boxes, use Japanese and PSM 7
            lang = 'jpn'
            # 7: Treat the image as a single text line.
            custom_config = r'--oem 3 --psm 7'
        
        # Use pytesseract to do OCR on the thresholded image, specifying the language and custom config
        text = pytesseract.image_to_string(Image.fromarray(thresh_image), lang=lang, config=custom_config)
        # Revised code to remove all whitespaces, including those in the middle
        text_strip = "".join(text.split())
        
        # display_image("thresh_image", thresh_image)
        print(f"text_strip: {text_strip}")
        # Append both the stripped text and its corresponding box coordinates
        results.append((text_strip, (x, y, w, h)))

    return results  # Return the list of tuples containing text and coordinates

def process_image_and_sort_text(image_path: str) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    # Detect text boxes in the image
    text_boxes = detect_boxes_in_image(image_path)
    
    # Extract text and positions from the detected boxes
    extracted_text_boxes = ocr_on_boxes(image_path, text_boxes)
    
    # Isolate the sentence for sorting and the associated word positions
    sentence_for_sorting = extracted_text_boxes[-1][0]  # Assuming the last box contains the sentence
    word_positions = extracted_text_boxes[:-1]  # Exclude the sentence box
    
    # Separate words for sorting process
    words_to_sort = [word for word, _ in word_positions]
    
    # Sort words based on the original sentence
    sorted_word_list = generate_sorted_sentence(words_to_sort, sentence_for_sorting)
    
    # Associate sorted words with their original positions
    word_position_mapping = {word: position for word, position in word_positions}
    sorted_text_boxes = [(word, word_position_mapping[word]) for word in sorted_word_list if word in word_position_mapping]
    
    return sorted_text_boxes

# ========= run this code ==========

# Example usage
if __name__ == "__main__":
    image_path = "demo_images/chi_jpn_2.jpg"
    boxes = process_image_and_sort_text(image_path)
    print(boxes)
        