"""
This will become a submodule to look up locations and other geocoding functions
"""

import geocoder
import geopandas

google_api_key ='AIzaSyCU1dIzmpwL6rxLMHhKuntmtK1TyFuBidk'

target_address = '52 Maney Ave, Asheville, NC'

# alternate provider
# loc1 = geocoder.osm(target_address).geojson
# print(loc1)

# http://geopandas.org/reference/geopandas.tools.geocode.html


df = geopandas.tools.geocode([target_address],
                             provider='nominatim',)

print(df)
print(type(df))