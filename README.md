# Opensim Oar file utilities
This archive contains a series of python scripts for working with oar files.  These oar files may be standard regions, or VAR regions.  Mega regions are rejected.  Multiple regions per archive may not behave correctly, as it was only written for single region per archive.

Displayed images are transposed vertically to match how the viewer and other tools present OpenSimulator maps, but the terrains are left in the correct implementation within the archives.

These scripts were written and tested on Ubuntu linux, but should work where-ever the correct python libraries can be installed.

## Dependencies
These are standard python scripts.  These dependencies were all present on a ubuntu desktop installation.

* sys
* tarfile
* StringIO
* struct
* xml.etree.cElementTree
* PIL

## Scripts
This section contains a short description of the scripts contained here, their inputs, and their output.

### split.py archive.oar

split.py will take the oar file from a VAR region, and will split it into regular sized region oar files.  It will reject oar files from mega regions, and standard sized regions.  Oar files with multiple regions contained were not tested, and will most likely not completely work.

split.py outputs a series of oar files, depending on how large the VAR region originally was.  The files will be named by appending X,Y.oar to the filename of the input oar, so that LargeRegion.oar will result in LargeRegion-0,0.oar, LargeRegion-0,1.oar, ...  X,Y are the region coordinates in relation to the lower-left corner of the VAR region.

The oar files may be loaded into standard OpenSimulator regions, and have their relative positions coded into their filenames. For Example, a 2x2 Var region split:

    |-------------|         |----------||----------|
    | region      |         |region-1,0||region-1,1|
    |             | ---->   |----------||----------|
    |0,0          |         |region-0,0||region-0,1|
    |-------------|         |----------||----------|



This script has been tested with success on VAR regions up to 6x6

### terrainInspector.py archive.oar

terrainInspector.py will take one or more archive files, and extract their terrain heightmaps.  It will display the image in a PIL window.

### objectInstector.py archive.oar

objectInspector.py will take one or more archives, generate an image file the same resolution as the region contained, and draw points in the image in the same locations as the objects on the region in question.  The image is displayed in a PIL window.

### combinedInspector.py archive.oar

combinedInspector.py will take one or more archives, and will overlay the terrainInspector.py and objectInspector.py images, displaying the result in a PIL window.

### Author: Michael Heilmann
### LICENCE: MIT
