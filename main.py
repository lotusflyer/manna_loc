import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
from urllib2 import urlopen
from zipfile import ZipFile
from io import BytesIO
import shapefile
from shapely.geometry import Point, Polygon
from json import dumps
import osr
import sys
import os
import contextily as ctx
import matplotlib.pyplot as plt
import geocoder

def add_basemap(ax, zoom, url='http://tile.stamen.com/terrain/tileZ/tileX/tileY.png'):
    xmin, xmax, ymin, ymax = ax.axis()
    basemap, extent = ctx.bounds2img(xmin, ymin, xmax, ymax, zoom=zoom, url=url)
    ax.imshow(basemap, extent=extent, interpolation='bilinear')
    # restore original x/y limits
    ax.axis((xmin, xmax, ymin, ymax))

# naming some of the projections we care about
mercator_crs = '3784' # mercator project distance in meters
grs80_lat_lng = 'GRS80' #census shape file -- lat long
wkn_lat_lng = '4326' # World Geodetic System used by GPS sats -- this is lat lng!!!
google_crs = '3857' # WGS 84 / Pseudo-Mercator -- Spherical Mercator, Google Maps, OpenStreetMap, Bing, ArcGIS, ESRI

fs_miles = 2
fs_meters = fs_miles * 1609.34
food_serving_area_radius = fs_meters
print("food sources serve people within {} meters or {} miles".format(food_serving_area_radius, fs_miles))

shapefile_dir = '../wnc_food_desert/mapping_geometry_apps/shape_file_dir/'


bun_geo = gpd.read_file(shapefile_dir + 'buncombe_bg.shp')
bun_geo = bun_geo.drop(['AFFGEOID', 'ALAND', 'AWATER', 'BLKGRPCE',
                        'COUNTYFP', 'LSAD', 'NAME', 'STATEFP', 'TRACTCE' ], axis=1)

# bun_geo = bun_geo.to_crs(epsg=mercator_crs)
print(bun_geo.crs)

loc = geocoder.osm('52 Maney Ave, Asheville, NC').geojson

# print(loc)
targ_latlng = loc['features'][0]['geometry']['coordinates']
print(targ_latlng)
print(type(targ_latlng))

pnt = Point(targ_latlng[0], targ_latlng[1])

# containing = None

for index, row in bun_geo.iterrows():
    res = pnt.within(row['geometry'])
    if res:
        print("Found Target in {}".format(row['GEOID'], res))
        # containing = row['geometry']

serving_area = pnt.buffer(food_serving_area_radius)


for index, row in bun_geo.iterrows():
    res = serving_area.intersection(row['geometry'])
    if res:
        print("Found intersection with {}".format(row['GEOID'], res))
        # containing = row['geometry']
