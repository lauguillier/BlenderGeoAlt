# Generate a mesh from a landscape coordinates in France and get the elevation from geoportail
# Laurent Guillier
# October 2020
# Use as is, at your own risk!

import bpy
import numpy
import json
import requests
import math
import time


# Coordinates of the selected area

# Oloron Sainte Marie
'''
west = -0.606585
north = 43.195645
east = -0.603585
south = 43.192090
'''
# La Rhune
'''
north = 43.319527
west = -1.652756
south = 43.319
east = -1.652
'''
# La Revellata, Corsica
north = 42.585322
west = 8.720999
south = 42.581024
east = 8.72734

nbstep = 125

# TODO : if nbstep is too high, the uri request is too long (http error 414)
# In this case, perform the operation on n terrain subdivision
# Also, horizontal resolution seems to be ~5m, so getting such a sampling length generates moiré on the mesh :/

# functions to convert WGS84 lat and lon to local cartesian X Y
# from https://gis.stackexchange.com/questions/325594/formula-to-convert-xyz-cartesian-to-latitude-longitude-using-wgs84
midlat = (north + south)/2
midlon = (east + west)/2
convergence = math.cos(midlat * (math.pi / 180.0))

def GeoToLocalX(lon):
    return (lon - midlon) * convergence  * 111120.0

def GeoToLocalY(lat):
    return (lat - midlat) * 111120.0


## Object
name = "land"
verts = []
faces = []


# get the elevation for each point

# Now we have to send request as
# https://wxs.ign.fr/choisirgeoportail/alti/rest/elevation.json?lon=-0.612232|-0.608039&lat=43.194681|43.194086

print ("Retrieving elevations on ign.fr")
start = time.time()
iter = 1

for lat in numpy.linspace(north, south, nbstep):
    cmd = 'https://wxs.ign.fr/choisirgeoportail/alti/rest/elevation.json?'
    arglon='lon='
    arglat='lat='+str(lat)
    for lon in numpy.linspace(west, east, nbstep):
        arg = '|'+str(lon) if lon != west else str(lon)
        arglon += arg
        arg = '|'+str(lat) if lon != east else ''
        arglat+= arg

    cmd += arglon+'&'+arglat
    #print(cmd)

    print("{}/{}".format(iter, nbstep), end='\r')
    iter += 1
    rq = requests.get(cmd)
    data = rq.json()
    
    for item in data['elevations']:
        x = GeoToLocalX(item['lon'])
        y = GeoToLocalY(item['lat'])
        z = item['z']
        #TODO : process acc in order to get worst / mean / best accuracy in the field
        
        verts.append([x, y, z])

    # Now create the faces
    for i in range(0, nbstep-1):
        for j in range(0, nbstep-1):
            faces.append((i*nbstep+j, i*nbstep+j+1, (i+1)*nbstep+j+1, (i+1)*nbstep+j))


# Create Mesh Datablock
mesh = bpy.data.meshes.new(name)
mesh.from_pydata(verts, [], faces)

# Create Object and link to scene
obj = bpy.data.objects.new(name, mesh)

# Links object to the master collection of the scene.
scene = bpy.context.scene
scene.collection.objects.link(obj)

# Select the object
bpy.context.view_layer.objects.active = obj

# Shade smooth
mesh = bpy.context.object.data
for f in mesh.polygons:
    f.use_smooth = True


# Add custom properties
obj["west"] = west
obj["east"] = east
obj["north"] = north
obj["south"] = south
obj["midlat"] = midlat
obj["midlon"] = midlon
obj["NWelevation"] = verts[0][2]
obj["NbStep"] = nbstep

end = time.time()

print("\nDone in {:.2f} sec".format(end - start))
