import cv2


def display_image(window_name, image):
    # Resize image for display if it's too large
    max_height = 600
    max_width = 800
    height, width = image.shape[:2]
    scaling_factor = min(max_width/width, max_height/height)
    if scaling_factor < 1:
        image = cv2.resize(image, None, fx=scaling_factor,
                           fy=scaling_factor, interpolation=cv2.INTER_AREA)
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
        cv2.putText(image, str(index), text_position,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the image with boxes
    display_image("Detected Boxes", image)
