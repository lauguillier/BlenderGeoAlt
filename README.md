# BlenderGeoAlt

## Overview
BlenderGeoAlt is a POC script for blender that generates a terrain from north/south/west/east coordinates, fetching the elevation information on french service GéoPortail with highly accurate vertical data (dm).

![La Rhune](BlenderGeoAlt.png  "La Rhune, Pays basque")

Obviously the terrain to modelise must be located in mainland France (including Corsica).
The purpose of this script is to get elevation accuracy on small terrains for architecture students. For large terrains, you'd better use [BlenderGIS](https://github.com/domlysz/BlenderGIS) add-on, which has rich and nice features.


## Usage

The script was written in blender 2.90.0.
Select 'Scripting' workspace tab in the top line, and load the script with menu 'Text/Open' (Alt-O).

At the moment, you have to enter the north/south/west/east coordinates within the python script source code:

	# La Rhune
	north = 43.319527
	west = -1.652756
	south = 43.3195
	east = -1.6527

You can get the coordinates you want by browsing the Géoportail website map ([https://www.geoportail.gouv.fr/carte](https://www.geoportail.gouv.fr/carte) ) and right-click on the selected coordinate to get the lat/long information:
![Geoportail](geoportail.png  "Geoportail")	


Then set SamplingLenght to indicates the target terrain division in x and y directions. Horizontal resolution is apparently about 5m, so do not choose a divider that's yeld a too close length unless you want to get moiré:
![Moiré due to horizontal oversampling](moire.png  "Moiré due to horizontale oversampling")

Click menu 'Text/Run Script' or Alt-P to run the script.

The resulting mesh coordinate units are meter. The mesh will be centered on (0,0) XY reference.
North is aligned with Y axis and east is aligned with X axis.
The Z value of each vertex is directly related to the fetched elevation from Géoportail. So look up for meshes in mountains ;)
Dimensions of the terrain are indicated in the Item panel under label 'Dimensions'.

Object custom properties are added:
- NWelevation is North/West vertex elevation
- midlat and midlon are latitude and longitude of the center point of the terrain
- north/south/west/east and NbStep are the input coordinates and nbstep used to generate the terrain
- NbXStep and NbYStep are the number of sampling on each axis
- Sampling X and Sampling Y are the sempling length on each axis
- Acc min, Acc max and Acc mean are statistics on retreived geoportail data accuracy

## TODO
This is just a POC to see how one can get and use precise elevation figures from Géoportail to modelise terrain in blender.

A lot of improvements could be made:
- automatic [done] and optimal nbstep setting according to terrain dimensions and moiré avoidance
- optimising access to the geoportail data server: the request length is proportional to nbstep, so error http 414 is frequently seen!
- code cleaning and refactoring: handling errors, defining functions...
- make sure WGS84 is the way to go, deal with other projections if required
- process "acc" field in order to get worst / mean / best accuracy in the field [done]
- add custom properties: min and max elevation
- evolution to a blender add-on with ui for parameters input
- ...

## Afterword
The generated terrain is quite disapointing regarding the horizontal resolution and moiré-ish patterns.
This may not be the way to go for getting precise elevation of a small terrain.