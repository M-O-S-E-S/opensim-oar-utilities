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

def showTerrain(src, count):
    for member in src.getmembers():
        if member.name.startswith("terrains"):
            terrain = tf.extractfile(member.name).read()

            img = Image.new('F', (count*256, count*256), "black")
            pixels = img.load()

            t = []
            c = 0
            while c < len(terrain):
                t.append(struct.unpack('f', ''.join(i for i in terrain[c:c+4])))
                c += 4

            for i in range(img.size[0]):
                for j in range(img.size[1]):
                    pixels[i,j] = t[i + j*img.size[0]][0]


            img.show()


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
                        showTerrain(tf, count)
                else:
                    print "invalid oar file"
            else:
                print "invalid oar file"
        except IOError, err:
            print '%20s %s' % (oarFile, err)
