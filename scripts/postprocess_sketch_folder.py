import os
import cv2
import shutil
import numpy as np
import glob
import ray
# ray.init()

from tqdm import tqdm

BUILDING_DATASET_ROOT = "/mnt/c/Users/Petingo/Desktop/animation/dataset"

@ray.remote
def run(filename):
    sketch = cv2.imread(filename)
    # sketch = cv2.GaussianBlur(sketch,(3,3),0)

    background_pixel = (sketch==[0, 255, 0]).all(axis=2)
    white_pixel = (sketch==[255, 255, 255]).all(axis=2)
    edge_pixel = np.ones_like(background_pixel, dtype='bool')
    edge_pixel = np.logical_xor(edge_pixel, background_pixel)
    edge_pixel = np.logical_xor(edge_pixel, white_pixel)

    sketch[background_pixel] = [0, 0, 0]
    sketch[white_pixel] = [0, 0, 0]
    sketch[edge_pixel] = [255, 255, 255]
    
    cv2.imwrite(filename, sketch)

files = glob.glob(os.path.join(BUILDING_DATASET_ROOT, "*.bmp"))
task = [run.remote(f) for f in files]
ray.get(task)

# run(files[0])
# print(os.path.join(BUILDING_DATASET_ROOT, "*.bmp"))
# print([ i for i in ])
# run(glob.glob(os.path.join(BUILDING_DATASET_ROOT, "*.bmp")[0]))、