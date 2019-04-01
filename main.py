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

# address to examine
target_address = '627 Swannanoa River Road Asheville, NC 28805-2445'

# naming some of the projections we care about
mercator_crs = '3784' # mercator project distance in meters
grs80_lat_lng = 'GRS80' #census shape file -- lat long
wkn_lat_lng = '4326' # World Geodetic System used by GPS sats -- this is lat lng!!!
google_crs = '3857' # WGS 84 / Pseudo-Mercator -- Spherical Mercator, Google Maps, OpenStreetMap, Bing, ArcGIS, ESRI

fs_miles = 50
fs_meters = fs_miles * 1609.34
food_serving_area_radius = fs_meters
print("food sources serve people within {} meters or {} miles".format(food_serving_area_radius, fs_miles))

shapefile_dir = '../wnc_food_desert/mapping_geometry_apps/shape_file_dir/'


bun_geo = gpd.read_file(shapefile_dir + 'buncombe_bg.shp')
bun_geo = bun_geo.drop(['AFFGEOID', 'ALAND', 'AWATER', 'BLKGRPCE',
                        'COUNTYFP', 'LSAD', 'NAME', 'STATEFP', 'TRACTCE' ], axis=1)

# bun_geo = bun_geo.to_crs(epsg=mercator_crs)


# f, ax = plt.subplots()
# bun_geo.plot(ax=ax, cmap='gist_earth')
# f.show()
# f.savefig("generated_maps/buncombe_bg.png")


print(bun_geo.crs)

target_loc= gpd.tools.geocode([target_address],
                             provider='nominatim',)

# we have a successful geocode
assert len(target_loc) > 0


bun_geo['within'] = target_loc.within(bun_geo)
print(bun_geo[bun_geo['within'] == True])


f, ax = plt.subplots(figsize=(8, 6))
bun_geo.plot(ax=ax, cmap='BrBG', alpha=0.2, edgecolor='k')
target_loc.plot(color='red', ax=ax, alpha=1.0, edgecolor='k')
f.show()
f.savefig("generated_maps/targ_address_with_bg.png")

circles = target_loc['geometry'].buffer(0.05)
circles_df = gpd.GeoDataFrame(circles)
circles_df.geometry = circles

f, ax = plt.subplots(figsize=(8, 6))
bun_geo.plot(ax=ax, cmap='BrBG', alpha=0.2, edgecolor='k')
circles_df.plot(color='red', ax=ax, alpha=1.0, edgecolor='k')
f.show()

food_coverage = gpd.overlay(bun_geo, circles_df, how='intersection')

f, ax = plt.subplots(figsize=(8, 6))
food_coverage.plot(ax=ax, cmap='BrBG', alpha=0.2, edgecolor='k')
# circles.plot(color='red', ax=ax, alpha=1.0, edgecolor='k')
f.show()