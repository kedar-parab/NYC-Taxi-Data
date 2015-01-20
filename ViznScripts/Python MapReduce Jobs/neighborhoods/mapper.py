#!/usr/bin/env python
import sys
sys.path.append('.')
import matplotlib
matplotlib.use('Agg')
from matplotlib.path import Path
from rtree import index as rtree
import numpy, shapefile, time

def findNeighborhood(location, index, neighborhoods):
    match = index.intersection((location[0], location[1], location[0], location[1]))
    for a in match:
        if any(map(lambda x: x.contains_point(location), neighborhoods[a][1])):
            return a
    return -1

def readNeighborhood(shapeFilename, index, neighborhoods):
    sf = shapefile.Reader(shapeFilename)
    for sr in sf.shapeRecords():
        if sr.record[1] not in ['New York', 'Kings', 'Queens', 'Bronx']: continue
        paths = map(Path, numpy.split(sr.shape.points, sr.shape.parts[1:]))
        bbox = paths[0].get_extents()
        map(bbox.update_from_path, paths[1:])
        index.insert(len(neighborhoods), list(bbox.get_points()[0])+list(bbox.get_points()[1]))
        neighborhoods.append((sr.record[3], paths))
    neighborhoods.append(('UNKNOWN', None))

def parseInput():
    for line in sys.stdin:
        line = line.strip('\n')
        values = line.split(',')
        if len(values)>1 and values[0]!='medallion': 
            yield values

def mapper():
    index = rtree.Index()
    neighborhoods = []
    readNeighborhood('ZillowNeighborhoods-NY.shp', index, neighborhoods)
    agg = {}
    agg1 = {}
    for values in parseInput():
        try:
            pickup_location = (float(values[10]), float(values[11]))
            dropoff_location = (float(values[12]), float(values[13]))
            pickup_neighborhood = findNeighborhood(pickup_location, index, neighborhoods)
            dropoff_neighborhood = findNeighborhood(dropoff_location, index, neighborhoods)
            #pick_drop_pair = "" + str(pickup_neighborhood) + ':' str(dropoff_neighborhood)
            if pickup_neighborhood!=-1 and dropoff_neighborhood!=-1:
                 agg[neighborhoods[pickup_neighborhood][0]+':'+neighborhoods[dropoff_neighborhood][0]] = agg.get(neighborhoods[pickup_neighborhood][0]+':'+neighborhoods[dropoff_neighborhood][0], 0) + 1
        except Exception, e:
            continue

    for item in agg.iteritems():
        print '%s\t%s' % (item[0], item[1])

if __name__=='__main__':
    mapper()
