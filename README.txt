Oar Splitter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This archive contains a series of python scripts for working with oar files.  These oar files may be standard regions, or VAR regions.  Mega regions are rejected.  Multiple regions per archive may not behave correctly, as it was only written for single region per archive.

These scripts were written and tested on Ubuntu linux.

split.y [archive]

split.py will take the oar file from a VAR region, and will split it into regular sized region oar files.  It strips all assets from the split oar files, so they will only work when reloaded into the same grid.

terrainInspector.py [archive ...]

terrainInspector.py will take one or more archive files, and will parse out and display their terrain file.

objectInstector.py [archive ...]

objectInspector.py will take one or more archives, generate an image file the same resolution as the region contained, and draw points in the image in the same locations as the objects on the region in question.

combinedInspector.py [archive ...]

combinedInspector.py will take one or more archives, and will overlay the terrainInspector.py and objectInspector.py images, displaying the result.

Author: Michael Heilmann
LICENCE: MIT
