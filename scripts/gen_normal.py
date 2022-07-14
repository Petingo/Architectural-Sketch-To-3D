import glob
from traceback import print_tb
import numpy as np
import open3d as o3d

if __name__ == "__main__":
    files = glob.glob("./to_print/*.obj")

    for filename in files:
        if "refined" in filename:
            continue

        if filename[:-4] + ".ply" in files:
            continue
        
        print(f"Loading {filename}")
        mesh = o3d.io.read_triangle_mesh(filename)
        pcd = mesh.sample_points_uniformly(number_of_points = 100000)
        pcd.estimate_normals()
        o3d.io.write_point_cloud(filename[:-4] + ".ply", pcd)