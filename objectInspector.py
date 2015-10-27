#!/usr/bin/python

from PIL import Image
import xml.etree.cElementTree as ET
import struct, sys, tarfile
from main import getRegionCount

def writeRegionObjects(src, img):
    pixels = img.load()
    for member in src.getmembers():
        if member.name.startswith("objects"):
            file = src.extractfile(member.name)
            tree = ET.fromstring(file.read().encode('utf-16-be'))
            xNode = tree.find('./SceneObjectPart/GroupPosition/X')
            x = int(float(xNode.text))
            yNode = tree.find('./SceneObjectPart/GroupPosition/Y')
            y = int(float(yNode.text))
            #skip off-region and therefore off-image objects
            if x < 0 or y < 0:
                continue
            if x >= img.size[0] or y >= img.size[0]:
                continue
            #print "%d, %d: %d" % (x,y, img.size[0])
            pixels[x,y] = 255.0

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
                        img = Image.new('F', (count*256, count*256), "black")
                        writeRegionObjects(tf, img)
                        img.show()
                else:
                    print "invalid oar file"
            else:
                print "invalid oar file"
        except IOError, err:
            print '%20s %s' % (oarFile, err)
