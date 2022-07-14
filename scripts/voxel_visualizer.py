#%%
import numpy as np
import matplotlib.pyplot as plt

from scipy.io import loadmat
#%%
def get_voxel_tensor(path):
    # ground truth voxel head to x, up to y
    # transform to be able to compare with the voxel converted by SoftRas
    voxel = loadmat(path)['Volume'].astype(np.float32)
    voxel = np.rot90(np.rot90(voxel, axes=(1, 0)), axes=(2, 1))
    
    return voxel
#%%

def obj_data_to_mesh3d(odata):
    """
    Code taken from https://stackoverflow.com/questions/59535205/plotly-mesh3d-plot-from-a-wavefront-obj-file
    """
    # odata is the string read from an obj file
    vertices = []
    faces = []
    lines = odata.splitlines()

    for line in lines:
        slist = line.split()
        if slist:
            if slist[0] == 'v':
                vertex = np.array(slist[1:], dtype=float)
                vertices.append(vertex)
            elif slist[0] == 'f':
                face = []
                for k in range(1, len(slist)):
                    face.append([int(s) for s in slist[k].replace('//','/').split('/')])
                if len(face) > 3: # triangulate the n-polyonal face, n>3
                    faces.extend([[face[0][0]-1, face[k][0]-1, face[k+1][0]-1] for k in range(1, len(face)-1)])
                else:
                    faces.append([face[j][0]-1 for j in range(len(face))])
            else: pass


    return np.array(vertices), np.array(faces)
#%%


points = np.load("points.npy")
print(points)

#%%

v = get_voxel_tensor("voxel.mat")
print(v)
#%%
# and plot everything
ax = plt.figure().add_subplot(projection='3d')
ax.voxels(v, edgecolor='k')

plt.show()
# %%
ax = plt.figure().add_subplot(projection='3d')
ax.scatter(points[:,0], points[:,1], points[:,2], edgecolor='k')

plt.show()

# %%
