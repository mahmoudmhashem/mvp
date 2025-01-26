import time

import cv2

from texture_utils import Rasterization
from utils import get_cube, get_homogeneous_matrix, get_model_matrix, get_next_camPos, get_orthographic_matrix, get_perspective_matrix, get_present_matrix, get_projection_matrix, get_vertex, get_view_matrix, present_cube, rotate
import numpy as np

from google.colab.patches import cv2_imshow
from IPython.display import clear_output

def draw_line(canvas: np.ndarray, start, end):
    color=(0, 0, 0)
    thickness=1
    cv2.line(canvas, start, end, color, thickness)

def draw_cube(canvas, cube_vertices):
    # Draw the edges of the cube
    edges = [(0, 1), (1, 2), (2, 3), (3, 0),  # Bottom edges
             (4, 5), (5, 6), (6, 7), (7, 4),  # Top edges
             (0, 4), (1, 5), (2, 6), (3, 7)]  # Vertical edges

    for edge in edges:
        start, end = cube_vertices[edge[0]], cube_vertices[edge[1]]
        draw_line(canvas, start, end)

def main():
    width, height ,depth = 800, 600, 1000
    # canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas = np.ones((width, height, 3), dtype=np.uint8) * 255

    raster = Rasterization(width, height)

    cube = get_cube()
    cube_H = get_homogeneous_matrix(cube)

    M1 = get_model_matrix([1, 0.5, 0.5], [0, 0, np.pi/2], [0, 0, 0])
    # M2 = get_model_matrix([1, 2, 1], [0, 0, 90], [10, 0, 0])

    n=0.9; f=20
    P_R = get_perspective_matrix(n, f)
    O_R = get_orthographic_matrix(n, f, -2, 2, -2, 2)

    camPos = np.array([0, 0, -1])
    while True:
        V_R = get_view_matrix(camPos) # , [0, 0, 0])
        camPos = get_next_camPos(camPos, [0, np.pi/9, 0])
        # camPos = get_next_camPos(camPos, [np.pi/9, 0, 0])

        projected_cube_H_w = P_R@O_R@V_R@M1@cube_H
        projected_cube_H = projected_cube_H_w / projected_cube_H_w[-1]
        # projected_cube_H = O_R@projected_cube_H

        projected_vertices_z = present_cube(projected_cube_H, width, height, depth, True, n, f, -2, 2, -2, 2)
        projected_vertices = present_cube(projected_cube_H, width, height, depth, False, n, f, -2, 2, -2, 2)

        # Draw the cube
        canvas = np.ones((width, height, 3), dtype=np.uint8) * 255 # delete all

        draw_cube(canvas, projected_vertices)
        raster.reset_z_buffer()
        raster.draw_texture(canvas, projected_vertices_z)
        
        cv2_imshow(canvas)
        clear_output(wait=True)
        

        # exit()
if __name__ == "__main__":
    main()
