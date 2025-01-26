import numpy as np
import cv2

# Create a white canvas
width, height = 800, 600
canvas = np.ones((height, width, 3), dtype=np.uint8) * 255

def draw_line(canvas, start, end, color=(0, 0, 0), thickness=2):
    """
    Draw a line on the canvas (NumPy array).

    :param canvas: The canvas (NumPy array) to draw on.
    :param start: The starting point of the line as a tuple (x, y).
    :param end: The ending point of the line as a tuple (x, y).
    :param color: The color of the line as a tuple (B, G, R). Default is black (0, 0, 0).
    :param thickness: The thickness of the line. Default is 2.
    """
    cv2.line(canvas, start, end, color, thickness)

# Example usage
start_point = (100, 100)
end_point = (700, 500)
draw_line(canvas, start_point, end_point, color=(255, 0, 0), thickness=3)

# Display the canvas
cv2.imshow('Canvas', canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()