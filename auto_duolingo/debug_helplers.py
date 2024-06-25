import cv2
import matplotlib.pyplot as plt


def display_image(window_name, image):
    # Convert BGR image to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize image for display if it's too large
    max_height = 600
    max_width = 800
    height, width = image.shape[:2]
    scaling_factor = min(max_width/width, max_height/height)
    if scaling_factor < 1:
        image = cv2.resize(image, None, fx=scaling_factor,
                           fy=scaling_factor, interpolation=cv2.INTER_AREA)

    # Display the image with matplotlib
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    plt.title(window_name)
    plt.axis('off')  # Hide axis
    plt.show()


def display_detected_boxes(image_path, boxes):
    # Load the image
    image = cv2.imread(image_path)

    # Draw each box on the image and mark the index
    for index, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # Position for the index text: slightly above and to the left of the box
        text_position = (x, y - 10 if y - 10 > 10 else y + 20)
        # Put the index number on the box with a larger font size
        cv2.putText(image, str(index), text_position,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the image with boxes
    display_image("Detected Boxes", image)
