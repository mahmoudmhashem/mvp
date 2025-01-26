import numpy as np

def get_cube():
      # Define the vertices of the cube
    cube = np.array([
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # Bottom vertices
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)       # Top vertices
    ])
    # cube = np.array([
    #     (-0.7, -0.7, 0.4), (0.7, -0.7, 0.4), (0.7, 0.7, 0.4), (-0.7, 0.7, 0.4),  # Bottom vertices
    #     (-0.7, -0.7, 0.8), (0.7, -0.7, 0.8), (0.7, 0.7, 0.8), (-0.7, 0.7, 0.8)       # Top vertices
    # ])
    # cube = np.array([
    #     (-0.7, -0.7, -0.8), (0.7, -0.7, -0.8), (0.7, 0.7, -0.8), (-0.7, 0.7, -0.8),  # Bottom vertices
    #     (-0.7, -0.7, 0.8), (0.7, -0.7, 0.8), (0.7, 0.7, 0.8), (-0.7, 0.7, 0.8)       # Top vertices
    # ])
    return cube

def rotate(matrix, thetah, axis="x"):
  Rx = np.array([
      [1, 0, 0],
      [0, np.cos(thetah), -np.sin(thetah)],
      [0, np.sin(thetah), np.cos(thetah)],
      ])

  Rx = np.array([
      [1, 0, 0],
      [0, np.cos(thetah), -np.sin(thetah)],
      [0, np.sin(thetah), np.cos(thetah)],
  ])

  Ry = np.array([
      [np.cos(thetah), 0, np.sin(thetah)],
      [0, 1, 0],
      [-np.sin(thetah), 0, np.cos(thetah)],
  ])

  Rz = np.array([
      [np.cos(thetah), -np.sin(thetah), 0],
      [np.sin(thetah), np.cos(thetah), 0],
      [0, 0, 1],
  ])
  if axis == "x":
    R = Rx
  elif axis == "y":
    R = Ry
  elif axis == "z":
    R = Rz
  else:
    print("Invalid axis, axis should be 'x', 'y' or 'z'")
  return (R@matrix.T).T

def translate(matrix, vector):
  T = np.eye(4)
  T[:3, 3] = np.array(vector)
  matrix = np.concatenate((matrix, np.ones((matrix.shape[0], 1))), axis=1)
  matrix = (T@matrix.T).T
  matrix = matrix[:, :3]
  return matrix

def get_rotation_matrix(thetahs):
  thetah_x, thetah_y, thetah_z = thetahs
  Rx = np.array([
      [1, 0, 0, 0],
      [0, np.cos(thetah_x), -np.sin(thetah_x), 0],
      [0, np.sin(thetah_x), np.cos(thetah_x), 0],
      [0, 0, 0, 1]
      ])

  Ry = np.array([
      [np.cos(thetah_y), 0, np.sin(thetah_y), 0],
      [0, 1, 0, 0],
      [-np.sin(thetah_y), 0, np.cos(thetah_y), 0],
      [0, 0, 0, 1]
  ])

  Rz = np.array([
      [np.cos(thetah_z), -np.sin(thetah_z), 0, 0],
      [np.sin(thetah_z), np.cos(thetah_z), 0, 0],
      [0, 0, 1, 0],
      [0, 0, 0, 1]
  ])
  # if axis == "x":
  #   R = Rx
  # elif axis == "y":
  #   R = Ry
  # elif axis == "z":
  #   R = Rz
  # else:
  #   print("Invalid axis, axis should be 'x', 'y' or 'z'")
  R = Rz@Ry@Rx
  return R

def get_translation_matrix(vector):
  T = np.eye(4)
  T[:3, 3] = np.array(vector)
  return T


def get_scale_matrix(width=1, height=1, depth=1):
    R = np.array([
        [width, 0, 0, 0],
        [0, height, 0, 0],
        [0, 0, depth, 0],
        [0, 0, 0, 1]
    ])
    return R

def get_model_matrix(scale, rotation, translation):
    R = get_rotation_matrix(rotation)
    T = get_translation_matrix(translation)
    S = get_scale_matrix(*scale)
    M = T@R@S
    return M

def get_homogeneous_matrix(vert):
  matrix = np.concatenate((vert, np.ones((vert.shape[0], 1))), axis=1)
  return matrix.T

def get_vertex(matrix):
  return matrix.T[:, :3]
  # return matrix[:, :3]


def get_view_matrix(cam_pos, target_pos=[0, 0, 0], up_vector=[0, 1, 0]):
    cam_pos = np.array(cam_pos)
    target_pos = np.array(target_pos)
    up_vector = np.array(up_vector)

    f = (target_pos - cam_pos)
    f = f / np.linalg.norm(f)

    up_vector = up_vector / np.linalg.norm(up_vector)

    s = np.cross(up_vector, f)
    s = s / np.linalg.norm(s)

    u = np.cross(s, f)

    R = np.concatenate((s.reshape(3, 1), u.reshape(3, 1), -f.reshape(3, 1)), axis=1)


    t = -R@(cam_pos.reshape(3, 1))

    v = np.concatenate((R, t), axis=1)
    V = np.concatenate((v, np.array([[0, 0, 0, 1]])), axis=0)

    return V


def present_cube(projected_cube_H, width, height, depth, return_z=False, n=0.001, f=1, l=-1, r=1, t=-1, b=1):
    present_matrix = get_present_matrix(width, height, depth, n, f, l, r, t, b)
    projected_cube_H = present_matrix@projected_cube_H
    projected_cube_H = projected_cube_H.astype(int)
    projected_cube = get_vertex(projected_cube_H)
    if not return_z:
        return projected_cube[:, :2]
    else:
       return projected_cube

# def get_perspective_matrix(fov, aspect_ratio, near_plane, far_plane):
#   P = np.array([
#       [1/(aspect_ratio*np.tan(fov/2)), 0, 0, 0],
#       [0, 1/np.tan(fov/2), 0, 0],
#       [0, 0, far_plane/(near_plane-far_plane), -near_plane*far_plane/(far_plane - near_plane)],
#       [0, 0, 1, 0]
#   ])
#   return P

# def get_orthographic_matrix(width, height, scale=200):
#     R = np.array([
#         [scale, 0, 0, width/2],
#         [0, scale, 0, height/2],
#         [0, 0, scale, 0],
#         [0, 0, 0, 1]
#     ])
#     return R



def get_present_matrix(width, height, depth, n=0.001, f=1, l=-1, r=1, t=-1, b=1):
    # orthographic projection matrix
    R = np.array([
        [1 / (r - l), 0, 0, -(l) / (r - l)],
        [0, 1 / (b - t), 0, -(t) / (b - t)],
        [0, 0, 1 / (f - n), -(n) / (f - n)],
        [0, 0, 0, 1]
    ])
    scale = get_scale_matrix(width, height, depth)
    return scale@R

def get_orthographic_matrix(n=0.001, f=1, l=-1, r=1, t=-1, b=1):
    # orthographic projection matrix
    R = np.array([
        [2 / (r - l), 0, 0, -(l + r) / (r - l)],
        [0, 2 / (b - t), 0, -(t + b) / (b - t)],
        [0, 0, 1 / (f - n), -(n +f) / (f - n)],
        [0, 0, 0, 1]
    ])
    return R

def get_perspective_matrix(n, f):
    # perspective projection matrix
    R = np.array([
        [n, 0, 0, 0],
        [0, n, 0, 0],
        [0, 0, f + n, -n * f],
        [0, 0, 1, 0]
    ])
    return R

def get_projection_matrix(fov, aspect_ratio, n, f):
    # perspective projection matrix
    R = np.array([
        [1/(np.tan(fov/2)*aspect_ratio), 0, 0, 0],
        [0, 1/np.tan(fov/2), 0, 0],
        [0, 0, f / (f - n), -f*n / (f - n)],
        [0, 0, 1, 0]
    ])
    return R

def get_next_camPos(camPos, rotation, speed=1):
    camPos = np.array(camPos)
    camPos_h = np.concatenate((camPos, np.array([1])), axis=0)
    R = get_rotation_matrix(rotation)
    camPos_h = R@camPos_h
    camPos = camPos_h[:-1]
    return camPos

# def get_projection_matrix(fov, aspect_ratio, n, f):
#     # perspective projection matrix
#     R = np.array([
#         [1/(np.tan(fov/2)*aspect_ratio), 0, 0, 0],
#         [0, 1/np.tan(fov/2), 0, 0],
#         [0, 0, -(f+n) / (f - n), -f*n / (f - n)],
#         [0, 0, -1, 0]
#     ])
#     return R
# def get_projection_matrix(fov, aspect_ratio, n, f):
#     # perspective projection matrix
#     R = np.array([
#         [1/(np.tan(fov/2)*aspect_ratio), 0, 0, 0],
#         [0, 1/np.tan(fov/2), 0, 0],
#         [0, 0, 1, -n],
#         [0, 0, 1, 0]
#     ])
#     return R