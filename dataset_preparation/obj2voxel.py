#%%
import enum
import os
import shutil 

import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm
from scipy.io import savemat, loadmat

from madcad.hashing import PositionMap
from madcad.io import read

DATASET_ROOT = "/mnt/c/Users/Petingo/Downloads/Building-Dataset-Generator/Simple-House-2"
OBJ_FILENAME = os.path.join(DATASET_ROOT, "{model_id}/model.obj")
MTL_FILENAME = os.path.join(DATASET_ROOT, "{model_id}/model.mtl")

# OBJ_NEW_FILENAME = os.path.join(DATASET_ROOT, "{model_id}/{model_id}.obj")
# MTL_NEW_FILENAME = os.path.join(DATASET_ROOT, "{model_id}/{model_id}.mtl")

VOXEL_FILENAME = os.path.join(DATASET_ROOT, "{model_id}/voxel.mat")

def get_voxel_tensor(path):
    # ground truth voxel head to x, up to y
    # transform to be able to compare with the voxel converted by SoftRas
    voxel = loadmat(path)['Volume'].astype(np.float32)
    voxel = np.rot90(np.rot90(voxel, axes=(1, 0)), axes=(2, 1))
    
    return voxel

for i in tqdm(range(4000, 5000)):
    # obj_filename = OBJ_FILENAME.format(model_id = i)
    # mtl_filename = MTL_FILENAME.format(model_id = i)

    obj_new_filename = OBJ_FILENAME.format(model_id = i)
    mtl_new_filename = MTL_FILENAME.format(model_id = i)

    voxel_filename = VOXEL_FILENAME.format(model_id = i)
    # if not os.path.exists(obj_new_filename):
    #     # Rename file
    #     shutil.move(obj_filename, obj_new_filename)
    #     shutil.move(mtl_filename, mtl_new_filename)

    min_ = [1e9, 1e9, 1e9]
    max_ = [-1e9, -1e9, -1e9]

    with open(obj_new_filename, 'r') as f:
        lines = f.readlines()
        
        for line in lines:
            if line[0] == 'v' and line[1] == ' ':
                val = line.split(' ')
                val = map(lambda x: float(x), val[1:])
                for i, data in enumerate(val):
                    min_[i] = min(min_[i], data)
                    max_[i] = max(min_[i], data)
        
        center = list(map(lambda x, y : (x + y) / 2, min_, max_))
    
    # load the obj file in a madcad Mesh
    mesh = read(obj_new_filename)
    
    # # choose the cell size of the voxel
    size = 1

    voxel = set()    # this is a sparse voxel
    hasher = PositionMap(size)   # ugly object creation, just to use one of its methods
    for face in mesh.faces:
        voxel.update(hasher.keysfor(mesh.facepoints(face)))

    v = np.zeros((32, 32, 32), dtype=int)

    for point in voxel:
        pos = [0, 0, 0]
        for i in range(3):
            pos[i] = min(max(int((point[i] - center[i]) / 128 * 32 + 16), 0), 31)

        v[tuple(pos)] = 1
    
    savemat(voxel_filename, {'Volume': list(v)})

    # v = get_voxel_tensor(voxel_filename)

    # ax = plt.figure().add_subplot(projection='3d')
    # ax.voxels(v, edgecolor='k')

    # plt.show()

    # print(voxel)
# %%
