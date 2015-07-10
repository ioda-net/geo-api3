# -*- coding: utf-8 -*-

import shputils
from os.path import dirname
from struct import unpack

import logging
log = logging.getLogger('chsdi')

# cache of GeoRaster instances in function of the layer name
_rasters = {}
_rasterfiles = {}

def get_raster(name):
    global _rasters
    result = _rasters.get(name, None)
    if not result:
        result = GeoRaster(_rasterfiles[name])
        _rasters[name] = result
    return result

def init_rasterfiles(datapath, preloadtypes):
    global _rasterfiles
    _rasterfiles = {
        'DTM25': datapath + 'dhm25_25_matrix/mm0001.shp',
        'DTM2': datapath + 'swissalti3d/2m/index.shp',
        'COMB': datapath + 'swissalti3d/kombo_2m_dhm25/index.shp'
    }
    try:
        for pt in preloadtypes:
            get_raster(pt)
    except Exception as e:
        log.error('Could not initialize raster files. Make sure they exist in the following directory: %s (Exception: %s)' % (datapath, e))


class Tile(object):
    def __init__(self, minX, minY, maxX, maxY, filename):
        self.minX=minX
        self.minY=minY
        self.maxX=maxX
        self.maxY=maxY
        self.filename=filename

    def contains(self, x, y):
        return self.minX<=x and self.maxX>x and self.minY<=y and self.maxY>y

    def __str__(self):
        return "%f, %f, %f, %f: %s" % (self.minX, self.minY, self.maxX, self.maxY, self.filename)

class BTTile(Tile):
    def getVal(self, x, y):
        file = open(self.filename, 'rb')
        if not hasattr(self, 'cols'):
            file.seek(10)
            (self.cols, self.rows, self.dataSize, self.floatingPoint)=unpack('<LLhh', file.read(12))
            self.resolutionX = (self.maxX-self.minX)/self.cols
            self.resolutionY = (self.maxY-self.minY)/self.rows

        posX=int((x-self.minX)/self.resolutionX)
        posY=int((y-self.minY)/self.resolutionY)
        file.seek(256+(posY+posX*self.rows)*self.dataSize)
        if self.floatingPoint==1:
          val=unpack("<f", file.read(self.dataSize))[0]
        else:
          if self.dataSize==2:
              format="<h"
          else:
              format="<l"
          val=unpack(format, file.read(self.dataSize))[0]

        file.close()
        return val

class GeoRaster:
    def __init__(self, shapefileName):
        self.tiles=[]
        shpRecords = shputils.loadShapefile(shapefileName)
        dir=dirname(shapefileName)
        if dir=="":
            dir="."
        for shape in shpRecords:
            filename=shape['dbf_data']['location'].rstrip()
            tileClass=None
            if filename.endswith(".bt"):
                tileClass=BTTile
            if not filename.startswith("/"):
                filename=dir+'/'+filename
            geo=shape['shp_data']
            tile=tileClass(geo['xmin'], geo['ymin'], geo['xmax'], geo['ymax'], filename)
            self.tiles.append(tile)

    def getVal(self, x,y):
        tile=self.getTile(x, y)
        if tile:
            return tile.getVal(x, y)
        else:
            return None

        #private
    def getTile(self, x, y):
        for cur in self.tiles:
            if cur.contains(x,y):
                return cur
        return None
