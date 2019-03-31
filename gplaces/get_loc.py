import geocoder

# google_api_key ='AIzaSyCU1dIzmpwL6rxLMHhKuntmtK1TyFuBidk'

# google is failing with request denied

# g = geocoder.osm('Mountain View, CA')
# # print(g.latlng)

def get_lat_lng(address):
    return geocoder.osm(address).wkt
