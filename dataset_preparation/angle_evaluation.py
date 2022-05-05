"""
This script takes azimuth and elevation as input and orient Rhino's view.

Input:
    x: azimuth
    y: elevation

"""

import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

import math

def spherical_to_Point3d(azimuth, elevation, radius=1):
    a = math.radians(azimuth)
    e = math.radians(elevation)
    
    x = radius * math.cos(a) * math.cos(e)
    y = radius * math.sin(a) * math.cos(e)
    z = radius * math.sin(e)
    
    return Rhino.Geometry.Point3d(x, y, z)

azimuth = x
elevation = y

targetLocation = Rhino.Geometry.Point3d(0, 0, 0)
cameraLocation = spherical_to_Point3d(azimuth, elevation, 200)

viewport = sc.doc.Views.ActiveView.ActiveViewport
viewport.SetCameraLocations(targetLocation, cameraLocation)
    