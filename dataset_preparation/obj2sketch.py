import os
import math
import random
import System
import shutil

from scriptcontext import doc

# Rhino Module
import Rhino
import rhinoscriptsyntax as rs

# Const variable Declaration
MODEL_COUNT = 1
SKETCHES_PER_MODEL = 20

EXPORT_W = 512
EXPORT_H = 512

CAM_DISTANCE = 320

DATASET_ROOT = "C:\\Users\\Petingo\\Downloads\\Building-Dataset-Generator"
IMPORT_FILENAME = os.path.join(DATASET_ROOT, "Models\\{model_id}.obj")
IMPORT_FILENAME_MTL = os.path.join(DATASET_ROOT, "Models\\{model_id}.mtl")

EXPORT_ROOT = os.path.join(DATASET_ROOT, "Building-Dataset\\{model_id}")
EXPORT_SKETCH_PATH = os.path.join(EXPORT_ROOT, "sketches")
EXPORT_FILENAME = os.path.join(EXPORT_SKETCH_PATH, "render_{sketch_id}.png")

EXPORT_VIEW_TXT_FILENAME = os.path.join(EXPORT_ROOT, "view.txt")

# Ref: https://destevez.net/2018/11/projection-of-a-sphere-onto-the-unit-sphere-in-spherical-coordinates/
def spherical_to_Point3d(azimuth, elevation, radius=1):
    a = math.radians(azimuth)
    e = math.radians(elevation)
    
    x = radius * math.cos(a) * math.cos(e)
    y = radius * math.sin(a) * math.cos(e)
    z = radius * math.sin(e)
    
    return Rhino.Geometry.Point3d(x, y, z)

def get_center_point(obj_filename):
    min_point = [1e9, 1e9, 1e9]
    max_point = [-1e9, -1e9, -1e9]
    
    with open(obj_filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line[0] == 'v' and line[1] == ' ':   # means it's a vertices
                data = line.split(' ')[1:]
                data = map(lambda x: float(x), data)
                for i, value in enumerate(data):
                    min_point[i] = min(min_point[i], data[i])
                    max_point[i] = max(max_point[i], data[i])
    
    center_point = []
    for i in range(3):
        center_point.append((min_point[i] + max_point[i]) / 2)
    
    # Map Z to Y
    center_point = [center_point[0], -center_point[2], center_point[1]]
    
#    transform_matrix = [[1, 0,  0],  \
#                        [0, 0, -1],  \
#                        [0, 1,  0]]  \
    
    return Rhino.Geometry.Point3d(center_point[0], center_point[1], center_point[2])

for model_id in range(MODEL_COUNT):
    
    if not os.path.exists(EXPORT_SKETCH_PATH.format(model_id=model_id)):
        os.makedirs(EXPORT_SKETCH_PATH.format(model_id=model_id))
    
    import_filename = IMPORT_FILENAME.format(model_id = model_id)
    import_filename_mtl = IMPORT_FILENAME_MTL.format(model_id = model_id)
    
    rs.Command("-_import {import_filename} _Enter".format(import_filename = import_filename))
    rs.Command("_SelAll _MeshToNURB _SelNone")
    rs.Command("_SelMesh _Delete")
    rs.Command("_BooleanUnion _SelAll _Enter")
    
    shutil.copyfile(import_filename, os.path.join(EXPORT_ROOT.format(model_id=model_id), "model.obj"))
    shutil.copyfile(import_filename_mtl, os.path.join(EXPORT_ROOT.format(model_id=model_id), "model.mtl"))
    
    center_point = get_center_point(import_filename)
    
    with open(EXPORT_VIEW_TXT_FILENAME.format(model_id=model_id), 'w') as view_txt:
        for sketch_id in range(SKETCHES_PER_MODEL):
            azimuth = random.randint(-180, 180)
            
            # side view
            if random.randint(0, 1) == 0:
                elevation = random.randint(0, 5)
            # other perspective
            else:
                elevation = random.randint(10, 60)
                
            # In view.txt:
            # azimuth elevation 0 distance
            view_txt.write("{a} {e} 0 {d}\n".format(a=azimuth, e=elevation, d=CAM_DISTANCE))
            
            targetLocation = center_point
            cameraLocation = spherical_to_Point3d(azimuth, elevation, CAM_DISTANCE)
            
            viewport = doc.Views.ActiveView.ActiveViewport
            viewport.SetCameraLocations(targetLocation, cameraLocation)
            
            # TODO: check Size() constructor
            image = doc.Views.ActiveView.CaptureToBitmap(System.Drawing.Size(EXPORT_W, EXPORT_H), Rhino.Display.DisplayModeDescription.GetDisplayMode(Rhino.Display.DisplayModeDescription.TechId))
            image.Save(EXPORT_FILENAME.format(model_id = model_id, sketch_id = sketch_id))
        
    rs.Command("_SelAll _Delete")
    