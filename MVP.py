import time
import tkinter as tk
from utils import get_cube, get_homogeneous_matrix, get_model_matrix, get_next_camPos, get_orthographic_matrix, get_perspective_matrix, get_present_matrix, get_projection_matrix, get_vertex, get_view_matrix, present_cube, rotate
import numpy as np

def draw_line(canvas: tk.Canvas, start, end):
    canvas.create_line(start[0], start[1], end[0], end[1])

def draw_cube(canvas, cube_vertices):
    # Draw the edges of the cube
    edges = [(0, 1), (1, 2), (2, 3), (3, 0),  # Bottom edges
             (4, 5), (5, 6), (6, 7), (7, 4),  # Top edges
             (0, 4), (1, 5), (2, 6), (3, 7)]  # Vertical edges

    for edge in edges:
        start, end = cube_vertices[edge[0]], cube_vertices[edge[1]]
        draw_line(canvas, start, end)

def main():
    root = tk.Tk()
    root.title("3D Cube with Tkinter")

    width, height = 800, 600
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    cube = get_cube()
    cube_H = get_homogeneous_matrix(cube)

    M1 = get_model_matrix([2, 2, 2], [0, 0, 0], [0, 0, 0])
    # M2 = get_model_matrix([1, 2, 1], [0, 0, 90], [10, 0, 0])

    n=0.5; f=3
    P_R = get_perspective_matrix(n, f)
    O_R = get_orthographic_matrix(n, f, -2, 2, -2, 2)

    camPos = np.array([0, 0, -1])
    while True:
        V_R = get_view_matrix(camPos) # , [0, 0, 0])
        camPos = get_next_camPos(camPos, [0, np.pi/9, 0])

        projected_cube_H_w = P_R@O_R@V_R@M1@cube_H
        projected_cube_H = projected_cube_H_w / projected_cube_H_w[-1]
        # projected_cube_H = O_R@projected_cube_H

        projected_vertices = present_cube(projected_cube_H, width, height)

        # Draw the cube
        canvas.delete("all")
        draw_cube(canvas, projected_vertices)
        root.update()
        root.update_idletasks()

        time.sleep(1)
if __name__ == "__main__":
    main()
