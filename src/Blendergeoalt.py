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
import statistics as stat


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
# target sampling lenght in meter
SamplingLenght = 10

#nbstep = 125

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


# Get terrain dimensions
lenght = GeoToLocalX(east) - GeoToLocalX(west)
width = GeoToLocalY(north) - GeoToLocalY(south)

# Determinate nbXstep and nbYstep to get SamplingLenght
nbXstep = round(lenght/SamplingLenght)
nbYstep = round(lenght/SamplingLenght)

print("Terrain lenght: {:.2f} - nbXstep = {} - actual sampling lenght: {:.2f}".format(lenght, nbXstep, lenght/nbXstep))
print("Terrain width: {:.2f} - nbYstep = {} - actual sampling lenght: {:.2f}".format(width, nbYstep, width/nbYstep))

## Blender Object
name = "land"
verts = []
faces = []

# accuracy
acc = []


# get the elevation for each point

# Now we have to send request as
# https://wxs.ign.fr/choisirgeoportail/alti/rest/elevation.json?lon=-0.612232|-0.608039&lat=43.194681|43.194086

print ("Retrieving elevations on ign.fr")
start = time.time()
iter = 1

for lat in numpy.linspace(north, south, nbYstep):
    cmd = 'https://wxs.ign.fr/choisirgeoportail/alti/rest/elevation.json?'
    arglon='lon='
    arglat='lat='+str(lat)
    for lon in numpy.linspace(west, east, nbXstep):
        arg = '|'+str(lon) if lon != west else str(lon)
        arglon += arg
        arg = '|'+str(lat) if lon != east else ''
        arglat += arg

    cmd += arglon+'&'+arglat
    #print(cmd)

    print("{}/{}".format(iter, nbYstep), end='\r')
    iter += 1
    rq = requests.get(cmd)
    try:
        data = rq.json()
    except ValueError:
        print("An error occured while getting the elevation data.\nReturned answer was:\n")
        print(rq)
        raise Exception("End of script")
    
    for item in data['elevations']:
        x = GeoToLocalX(item['lon'])
        y = GeoToLocalY(item['lat'])
        z = item['z']
        
        verts.append([x, y, z])
        acc.append(item['acc'])

    # Now create the faces
    for i in range(0, nbXstep-1):
        for j in range(0, nbYstep-1):
            faces.append((i*nbXstep+j, i*nbXstep+j+1,
                         (i+1)*nbXstep+j+1, (i+1)*nbXstep+j))


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
obj["NbXStep"] = nbXstep
obj["NbYStep"] = nbYstep
obj["Sampling X"] = lenght/nbXstep
obj["Sampling Y"] = width/nbYstep
obj["Acc min"] = min(acc)
obj["Acc max"] = max(acc)
obj["Acc mean"] = stat.mean(acc)

end = time.time()

print("\nDone in {:.2f} sec".format(end - start))
