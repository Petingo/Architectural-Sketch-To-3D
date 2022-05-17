import copy
from cv2 import cv2
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

img_width, img_height = (1920, 1080)
pcd = o3d.io.read_triangle_mesh('model.obj')

renderer_pc = o3d.visualization.rendering.OffscreenRenderer(img_width, img_height)
renderer_pc.scene.set_background(np.array([0, 0, 0, 0]))

# Optionally set the camera field of view (to zoom in a bit)
vertical_field_of_view = 15.0  # between 5 and 90 degrees
aspect_ratio = img_width / img_height  # azimuth over elevation
near_plane = 0.1
far_plane = 50.0
fov_type = o3d.visualization.rendering.Camera.FovType.Vertical
renderer_pc.scene.camera.set_projection(vertical_field_of_view, aspect_ratio, near_plane, far_plane, fov_type)

# Look at the origin from the front (along the -Z direction, into the screen), with Y as Up.
center = [0, 0, 0]  # look_at target
eye = [0, 0, 2]  # camera position
up = [0, 1, 0]  # camera orientation
renderer_pc.scene.camera.look_at(center, eye, up)

depth_image = np.asarray(renderer_pc.render_to_depth_image())
np.save('depth', depth_image)

normalized_image = (depth_image - depth_image.min()) / (depth_image.max() - depth_image.min())
plt.imshow(normalized_image)
plt.savefig('depth.png')