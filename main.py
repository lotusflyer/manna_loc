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

fs_miles = 2
fs_meters = fs_miles * 1609.34
food_serving_area_radius = fs_meters
# print("food sources serve people within {} meters or {} miles".format(food_serving_area_radius, fs_miles))

shapefile_dir = '../wnc_food_desert/mapping_geometry_apps/shape_file_dir/'


bun_geo = gpd.read_file(shapefile_dir + 'buncombe_bg.shp')
bun_geo = bun_geo.drop(['AFFGEOID', 'ALAND', 'AWATER', 'BLKGRPCE',
                        'COUNTYFP', 'LSAD', 'NAME', 'STATEFP', 'TRACTCE' ], axis=1)


# bun_geo = bun_geo.to_crs(epsg=mercator_crs)
# print("bun geo crs " + bun_geo.crs['init'])
# print(bun_geo.crs)

# this should be in meters since we are using mercator
bun_geo['area'] = bun_geo['geometry'].area

# f, ax = plt.subplots()
# bun_geo.plot(ax=ax, cmap='gist_earth')
# f.show()
# f.savefig("generated_maps/buncombe_bg.png")

target_loc= gpd.tools.geocode([target_address],
                             provider='nominatim',)



# we have a successful geocode
assert len(target_loc) > 0

# f, ax = plt.subplots(figsize=(8, 6))
# bun_geo.plot(ax=ax, cmap='BrBG', alpha=0.2, edgecolor='k')
# target_loc.plot(color='red', ax=ax, alpha=1.0, edgecolor='k')
# f.show()
# f.savefig("generated_maps/targ_address_with_bg.png")
# print("geocode crs " + target_loc.crs['init'])
# target_loc.to_crs(epsg=mercator_crs)

# make a dataframe
target_pnts_df = gpd.GeoDataFrame(target_loc)
# set it to mercator
# target_pnts_df.crs = {'init' : mercator_crs}
#target_pnts_df.to_crs(epsg=mercator_crs)

circles = target_pnts_df['geometry'].buffer(0.05)
circles_df = gpd.GeoDataFrame(circles)
circles_df.geometry = circles
circles_df.crs = {'init' : 'GRS80'}
# print("circles df crs " + circles_df.crs['init'])
#
f, ax = plt.subplots(figsize=(8, 6))
bun_geo.plot(ax=ax, cmap='BrBG', alpha=0.2, edgecolor='k')
circles_df.plot(color='red', ax=ax, alpha=1.0, edgecolor='k')
f.show()

food_coverage = gpd.overlay(bun_geo, circles_df, how='intersection')

f, ax = plt.subplots(figsize=(8, 6))
food_coverage.plot(ax=ax, cmap='BrBG', alpha=0.2, edgecolor='k')
# circles.plot(color='red', ax=ax, alpha=1.0, edgecolor='k')
f.show()

food_coverage['covered_area'] = food_coverage['geometry'].area

food_coverage_df = food_coverage[['GEOID', 'covered_area']]
food_coverage_df.index = food_coverage_df['GEOID'].astype(str)
food_coverage_df = food_coverage_df.drop(['GEOID'], axis=1)
# print(food_coverage_df.head(2))

all_area_df = bun_geo[['GEOID', 'area', 'geometry']]
all_area_df.index = all_area_df['GEOID'].astype(str)
all_area_df = all_area_df.drop(['GEOID'], axis=1)

bg_demograph_df = pd.read_csv('../wnc_food_desert/census_data_extracts/block_group_demographics.csv')
bg_demograph_df.index = bg_demograph_df['GEOID'].astype(str)
bg_demograph_df = bg_demograph_df.drop(['GEOID'], axis=1)
# print(bg_demograph_df.head())

result_df = food_coverage_df.join(all_area_df)

food_coverage.index = food_coverage['GEOID']

result_df = food_coverage.join(bg_demograph_df)

result_df['covered_ratio'] = (result_df['covered_area'] / result_df['area'])
result_df['percent_covered'] = result_df['covered_ratio'] * 100.
result_df['percent_covered'] = result_df['percent_covered'].apply(round)

# top_ten = gpd.GeoDataFrame(  result_df.sort_values('percent_covered', ascending=False)[:10] )
# print(top_ten['percent_covered'])

result_df['covered_pop'] = (result_df['covered_ratio'] * result_df['population']).apply(round).apply(int)

result_df['num_unemp'] = (result_df['covered_pop']  *
                          (result_df['percent_unemployed']/100)).apply(round).apply(int)
result_df['num_nohs'] = (result_df['covered_pop']  *
                          (result_df['percent_nohs']/100)).apply(round).apply(int)
result_df['num_inc_under_50'] = (result_df['covered_pop']  *
                          (result_df['percent income under 50K']/100)).apply(round).apply(int)



# print(result_df[['covered_pop', 'num_unemp', 'num_nohs', 'num_inc_under_50' ]])

print('----------------------------------------------------')
print("Summary results")
print('----------------------------------------------------')

print('At {}'.format(target_address))
print('Number of involved block groups \t {}'.format(len(result_df)))
print("People living in this area\t {}".format(result_df['covered_pop'].sum()))
print("With income under 50K: \t {}".format(result_df['num_inc_under_50'].sum()))
print("Unemployed living in this area\t {}".format(result_df['num_unemp'].sum()))
print("Without high school education \t {}".format(result_df['num_nohs'].sum()))




