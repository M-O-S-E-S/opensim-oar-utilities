#!/usr/bin/python

import sys, tarfile, StringIO, struct
import xml.etree.cElementTree as ET
from PIL import Image


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


archiveXML = '''<?xml version="1.0" encoding="utf-16"?>
<archive major_version="0" minor_version="8">
  <creation_info>
    <datetime>1445000494</datetime>
  </creation_info>
  <assets_included>False</assets_included>
  <region_info>
    <is_megaregion>False</is_megaregion>
    <size_in_meters>256,256</size_in_meters>
  </region_info>
</archive>'''

def copyLandData(src, dst, x, y):
    print "land data block %d, %d" % (x, y)
    # land data is stored in xml files, with an internal bitmap declaring parcel extents
    # we dont really parcel, so I am copying this wholesale
    # should the land be parcelled, the bitmap will have to be parsed and re-scaled

    # parcel uuids are supposed to be globally unique, but you can reload the same oar
    # repeatedly.  Assumption: Opensim handles this automagically
    for member in src.getmembers():
        if member.name.startswith("landdata"):
            dst.addfile(member, src.extractfile(member.name))

def copyRegionObjects(src, dst, offset_x, offset_y):
    print "objects block %d, %d" % (offset_x, offset_y)
    # objects are the primary operative here.  We must translate them, and cull
    # those that are outside of the region boundaries.  This will prevent any
    # off-region objects in the original from being transferred to the split regions
    # we are ignoring that for now
    copiedObjects = 0
    skippedObjects = 0
    for member in src.getmembers():
        if member.name.startswith("objects"):
            file = tf.extractfile(member.name)
            tree = ET.fromstring(file.read().encode('utf-16-be'))
            xNode = tree.find('./SceneObjectPart/GroupPosition/X')
            x = float(xNode.text) - offset_x
            yNode = tree.find('./SceneObjectPart/GroupPosition/Y')
            y = float(yNode.text) - offset_y
            if x < 0 or x > 255:
                skippedObjects += 1
                continue
            if y < 0 or y > 255:
                skippedObjects += 1
                continue

            xNode.text = str(x)
            yNode.text = str(y)
            otherParts = tree.find('./OtherParts/SceneObjectPart/GroupPosition')
            if otherParts is not None:
                for elem in otherParts:
                    if elem.tag == "X":
                        elem.text = str(float(elem.text) - x)
                    if elem.tag == "Y":
                        elem.text = str(float(elem.text) - y)
            xmlString = ET.tostring(tree)
            archiveFile = StringIO.StringIO(xmlString)
            info = tarfile.TarInfo(name=member.name)
            info.size = len(archiveFile.buf)
            dst.addfile(tarinfo=info, fileobj=archiveFile)
            copiedObjects += 1
    print "Skipped %d objects" % skippedObjects
    print "Copied %d objects" % copiedObjects

terrainCache = {}

def copyTerrain(src, dst, x, y, count):
    print "region terrain block %d, %d" % (x, y)
    for member in src.getmembers():
        if member.name.startswith("terrains"):
            img = None
            if member.name in terrainCache:
                img = terrainCache[member.name]
            else:
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
                        pixels[i,j] = t[j + i*img.size[0]][0]

                terrainCache[member.name] = img

            img = img.crop( (x,y,x+256,y+256) )

            pixels = img.load()
            imgString = ''
            for i in range(img.size[0]):
                for j in range(img.size[1]):
                    imgString += struct.pack('f', pixels[i,j])

            archiveFile = StringIO.StringIO(imgString)
            info = tarfile.TarInfo(name=member.name)
            info.size = len(archiveFile.buf)
            dst.addfile(tarinfo=info, fileobj=archiveFile)


def copyRegionSettings(src, dst, x, y):
    print "region settings block %d, %d" % (x, y)
    # region settings appear to just be global, langind pionts etc are unknown at this point
    # just copy them across

    #settings like elevation* are undocumented, ignore until testing proves otherwise
    for member in src.getmembers():
        if member.name.startswith("settings"):
            dst.addfile(member, src.extractfile(member.name))

def splitArchive(tf, rootName, count):
    print "Splitting the oarfile"
    for x in range(count):
        for y in range(count):
            oarName = "%s-%d,%d.tar.gz" % (rootName, x, y)
            print "Creating oar %s" % oarName
            nf = tarfile.open(oarName, "w:gz")
            archiveFile = StringIO.StringIO(archiveXML)
            info = tarfile.TarInfo(name="archive.xml")
            info.size = len(archiveFile.buf)
            nf.addfile(tarinfo=info, fileobj=archiveFile)
            copyLandData(tf, nf, x*256, y*256)
            copyRegionSettings(tf, nf, x*256, y*256)
            copyRegionObjects(tf, nf, x*256, y*256)
            copyTerrain(tf, nf, x*256, y*256, count)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Error usage: oarSplitter.py filename.oar"
        exit(1)
    oarFile = sys.argv[1]
    if not oarFile.endswith(".oar"):
        print "Error: archive does not have the correct file extension"
        exit(1)
    try:
        valid = tarfile.is_tarfile(oarFile)
        if valid:
            tf = tarfile.open(oarFile, mode="r:gz")
            if tf.firstmember.name == "archive.xml":
                count = getRegionCount(tf)
                if count < 1:
                    print "This is not a var-region archive, refusing to split"
                elif count == 1:
                    print "This is a standard archive, not splitting"
                else:
                    print "Var region detected containing %d region spaces" % (count*count)
                    splitArchive(tf, oarFile[:-4], count)
            else:
                print "invalid oar file"
        else:
            print "invalid oar file"
    except IOError, err:
        print '%20s %s' % (oarFile, err)

    print "complete"
