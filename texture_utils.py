from concurrent.futures import ThreadPoolExecutor, as_completed, wait
import cv2
import numpy as np


class Rasterization:
    def __init__(self, canvas_width, canvas_height):
        self.top_texture = cv2.imread("top-view.jpg")
        self.side_texture = cv2.imread("side_View.jpg")
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.reset_z_buffer()

    def get_cube_side_faces(self, vertices) -> np.ndarray:
        # Extract vertices for readability
        # FBL, FBR, FTR, FTL, BBL, BBR, BTR, BTL = vertices
        FTR, FTL, FBL, FBR, BTR, BTL, BBL, BBR = vertices
        
        # Define the side faces
        left_face = [FTL, FBL, BBL, BTL]     # Front Top-Left, Front Bottom-Left, Back Bottom-Left, Back Top-Left
        right_face = [FTR, FBR, BBR, BTR]    # Front Top-Right, Front Bottom-Right, Back Bottom-Right, Back Top-Right
        top_face = [FTL, FTR, BTR, BTL]      # Front Top-Left, Front Top-Right, Back Top-Right, Back Top-Left
        bottom_face = [FBL, FBR, BBR, BBL]   # Front Bottom-Left, Front Bottom-Right, Back Bottom-Right, Back Bottom-Left
        
        # Return the side faces
        faces = np.array([left_face, right_face, top_face, bottom_face])
        return faces

    def reset_z_buffer(self):
        self.z_buffer = np.full((self.canvas_height, self.canvas_width), float('inf'))  # Initialize z-buffer with infinity

    def get_cube_front_back_faces(self, vertices):
        # Extract vertices for readability
        # FBL, FBR, FTR, FTL, BBL, BBR, BTR, BTL = vertices
        FTR, FTL, FBL, FBR, BTR, BTL, BBL, BBR = vertices
        
        # Define the front and back faces
        front_face = [FTL, FTR, FBR, FBL]    # Front Top-Left, Front Top-Right, Front Bottom-Right, Front Bottom-Left
        back_face = [BTL, BTR, BBR, BBL]     # Back Top-Left, Back Top-Right, Back Bottom-Right, Back Bottom-Left
        
        # Return the front and back faces
        return np.array([front_face, back_face])

    def interpolate_point(self, x1, y1, z1, x2, y2, z2, t):
        x = (1 - t) * x1 + t * x2
        y = (1 - t) * y1 + t * y2
        z = (1 - t) * z1 + t * z2
        return (x, y, z)

    def get_color(self, u, v, texture: np.ndarray):
        texture_height, texture_width, _ = texture.shape
        texture_x = int(u * texture_width) % texture_width
        texture_y = int(v * texture_height) % texture_height
        color = texture[texture_y, texture_x]  # BGR format
        return color # color[::-1]  # Convert to RGB

    def interpolate_xz(self, y, x_start, y_start, z_start, x_end, y_end, z_end):
        if y_end == y_start:  # Avoid division by zero
            return x_start, z_start
        t = (y - y_start) / (y_end - y_start)
        x = x_start + t * (x_end - x_start)
        z = z_start + t * (z_end - z_start)
        return int(x), z

    def intersected(self, y, line):
        (x1, y1, _), (x2, y2, _) = line
        return (y1 <= y <= y2) or (y2 <= y <= y1)

    def draw_face(self, canvas: np.ndarray, texture, face):
        TL, TR, BR, BL = face
        edges = [
            (TL, TR),
            (TR, BR),
            (BR, BL),
            (BL, TL)
        ]

        face_copy = np.copy(face)
        sorted_indices = face_copy[:, 1].argsort()
        face_copy = face_copy[sorted_indices]
        y_min = int(face_copy[0, 1])
        y_max = int(face_copy[-1, 1])

        for y in range(y_min + 1, y_max):  # Scan from top to bottom
            intersections = []
            for edge in edges:
                if self.intersected(y, edge):
                    (x1, y1, z1), (x2, y2, z2) = edge
                    x, z = self.interpolate_xz(y, x1, y1, z1, x2, y2, z2)
                    intersections.append((x, z))

            intersections = sorted(intersections, key=lambda p: p[0])  # Sort by x-coordinate
            if len(intersections) < 2:
                continue

            x_start, z_start = intersections[0]
            x_end, z_end = intersections[-1]

            for x in range(x_start, x_end):
                t = (x - x_start) / (x_end - x_start)
                z = z_start + t * (z_end - z_start)
                if 0 <= x < self.z_buffer.shape[1] and 0 <= y < self.z_buffer.shape[0]:
                    if z < self.z_buffer[y, x]:  # Check z-buffer
                        self.z_buffer[y, x] = z
                        u = (x - x_start) / (x_end - x_start)
                        v = (y - y_min) / (y_max - y_min)
                        color = self.get_color(u, v, texture)
                        
                        canvas[y:y+1, x:x+1, :] = color

    def draw_texture(self, canvas: np.ndarray, cube_vertices):
        side_faces = self.get_cube_side_faces(cube_vertices)
        front_back_faces = self.get_cube_front_back_faces(cube_vertices)
        # with ThreadPoolExecutor(100) as executor:
        #     futures = []
        #     for face in side_faces:
        #         futures.append(executor.submit(self.draw_face, canvas, self.side_texture, face))
            
        #     for face in front_back_faces:
        #         futures.append(executor.submit(self.draw_face, canvas, self.top_texture, face))

        #     # Wait for all futures to complete
        #     # wait(futures)
        #     for future in as_completed(futures): 
        #         try: 
        #             future.result() # This will raise an exception if the task failed 
        #         except Exception as e: 
        #             print(f"Task generated an exception: {e}")
        for face in side_faces:
            self.draw_face(canvas, self.side_texture, face)

        for face in front_back_faces:
            self.draw_face(canvas, self.top_texture, face)

# import tkinter as tk
# import numpy as np
# import cv2

# class Rasterization:
#     def __init__(self):
#         self.top_texture = cv2.imread("top-view.jpg")
#         self.side_texture = cv2.imread("side_View.jpg")
#     def get_cube_side_faces(self, vertices) -> np.ndarray:
#         # Extract vertices for readability
#         # FBL, FBR, FTR, FTL, BBL, BBR, BTR, BTL = vertices
#         FTR, FTL, FBL, FBR, BTR, BTL, BBL, BBR = vertices
        
#         # Define the side faces
#         left_face = [FTL, FBL, BBL, BTL]     # Front Top-Left, Front Bottom-Left, Back Bottom-Left, Back Top-Left
#         right_face = [FTR, FBR, BBR, BTR]    # Front Top-Right, Front Bottom-Right, Back Bottom-Right, Back Top-Right
#         top_face = [FTL, FTR, BTR, BTL]      # Front Top-Left, Front Top-Right, Back Top-Right, Back Top-Left
#         bottom_face = [FBL, FBR, BBR, BBL]   # Front Bottom-Left, Front Bottom-Right, Back Bottom-Right, Back Bottom-Left
        
#         # Return the side faces
#         faces = np.array([left_face, right_face, top_face, bottom_face])
#         return faces

#     def get_cube_front_back_faces(self, vertices):
#         # Extract vertices for readability
#         # FBL, FBR, FTR, FTL, BBL, BBR, BTR, BTL = vertices
#         FTR, FTL, FBL, FBR, BTR, BTL, BBL, BBR = vertices
        
#         # Define the front and back faces
#         front_face = [FTL, FTR, FBR, FBL]    # Front Top-Left, Front Top-Right, Front Bottom-Right, Front Bottom-Left
#         back_face = [BTL, BTR, BBR, BBL]     # Back Top-Left, Back Top-Right, Back Bottom-Right, Back Bottom-Left
        
#         # Return the front and back faces
#         return np.array([front_face, back_face])

#     def interpolate_point(self, x1, y1, x2, y2, t):
#         x = (1 - t) * x1 + t * x2
#         y = (1 - t) * y1 + t * y2
#         return (x, y)

#     def get_color(self, u, v, texture:np.ndarray):
#         # Open the texture image
#         texture_height, texture_width, c = texture.shape
#         texture_x = int(u * texture_width) % texture_width
#         texture_y = int(v * texture_height) % texture_height
#         color = texture[texture_y, texture_x] # BGR format
#         return color[::-1] # Return in RGB format

#     def interpolate_x(self, y, x_start, y_start, x_end, y_end):
#         if y_end == y_start:  # Avoid division by zero
#             return x_start
#         return int(x_start + (y - y_start) * (x_end - x_start) / (y_end - y_start))

#     def intersected(self, y, line):
#         (x1, y1), (x2, y2) = line
#         return (y1 <= y <= y2) or (y2 <= y <= y1)

#     def draw_face(self, canvas: tk.Canvas, texture, face):
#             TL, TR, BR, BL = face
#             top_edge = np.array([TL, TR])
#             bottom_edge = np.array([BL, BR])
#             left_edge = np.array([TL, BL])
#             right_edge = np.array([TR, BR])
#             edges = [top_edge, bottom_edge, left_edge, right_edge]
            
#             face_copy = np.copy(face)
#             sorted_indices = face_copy[:, 1].argsort()
#             face_copy = face_copy[sorted_indices]
#             y_min = face_copy[0, 1]
#             y_max = face_copy[-1, 1]

#             for y in range(y_min+1, y_max): # scan from top to bottom
#                 intersections_x = set([])
#                 for edge in edges:
#                     if self.intersected(y, edge):
#                         (x1, y1), (x2, y2) = edge
#                         x = self.interpolate_x(y, x1, y1, x2, y2)
#                         intersections_x.add(x)

#                 intersections_x = sorted(intersections_x)
#                 # print(len(intersections_x))
#                 # print(intersections_x)

#                 if len(intersections_x) < 2:
#                     continue
#                 for x in range(intersections_x[0]+1, intersections_x[-1]):
#                     u = (x - intersections_x[0]) / (intersections_x[-1] - intersections_x[0])
#                     v = (y - y_min) / (y_max - y_min)
#                     color = self.get_color(u, v, texture)
#                     # canvas.create_rectangle(x, y, x+1, y+1, fill="#%02x%02x%02x" % tuple(color))
#                     # canvas.create_rectangle(x, y, x+1, y+1, fill="#%02x%02x%02x" % tuple((255, 0, 0)))
#                     canvas.create_rectangle(x, y, x+1, y+1, fill="#%02x%02x%02x" % tuple(color), outline="#%02x%02x%02x" % tuple(color))

#     def draw_texture(self, canvas: tk.Canvas, cube_vertices):

#         side_faces = self.get_cube_side_faces(cube_vertices)
#         front_back_faces = self.get_cube_front_back_faces(cube_vertices)

#         for face in side_faces:
#             self.draw_face(canvas, self.side_texture, face)

#         for face in front_back_faces:
#             self.draw_face(canvas, self.top_texture, face)