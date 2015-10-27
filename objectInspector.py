#!/usr/bin/python

from PIL import Image
import xml.etree.cElementTree as ET
import struct, sys, tarfile

def getRegionCount(tf):
    file = tf.extractfile(tf.firstmember)
    tree = ET.fromstring(file.read().encode('utf-16-be'))
    info = tree.find("region_info")
    if info.find("is_megaregion").text == "True":
        # we cannot split megaregions
        return -1
    x,y = info.find("size_in_meters").text.split(",")
    x = int(x)
    y = int(y)
    if x != y:
        # var regions are only round
        return -1
    return x/256

def writeRegionObjects(src, img):
    pixels = img.load()
    for member in src.getmembers():
        if member.name.startswith("objects"):
            file = tf.extractfile(member.name)
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
