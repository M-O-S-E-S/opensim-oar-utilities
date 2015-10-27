#!/usr/bin/python

from terrainInspector import drawTerrain
from objectInspector import writeRegionObjects
from split import getRegionCount
from PIL import Image
import sys, tarfile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Error usage: oarSplitter.py filename.oar"
        exit(1)
    for oarFile in sys.argv[1:]:
        try:
            valid = tarfile.is_tarfile(oarFile)
            if valid:
                tf = tarfile.open(oarFile, mode="r:gz")
                if tf.firstmember.name == "archive.xml":
                    count = getRegionCount(tf)
                    if count < 1:
                        print "This is not a var-region archive, refusing to split"
                    else:
                        img = drawTerrain(tf, count)
                        writeRegionObjects(tf, img)
                        img = img.transpose(Image.FLIP_TOP_BOTTOM)
                        img.show(title=oarFile)
                else:
                    print "invalid oar file"
            else:
                print "invalid oar file"
        except IOError, err:
            print '%20s %s' % (oarFile, err)
