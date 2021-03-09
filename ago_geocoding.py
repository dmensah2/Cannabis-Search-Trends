#import modules
from arcgis.gis import GIS
from arcgis.geocoding import geocode
from tkinter.filedialog import asksaveasfile
import geopandas as gpd

#connect to ArcGIS Online as anonymous user
gis = GIS()

# reverse geocode addresses from lat/longs
def ago_geocode(df, address):
    # convert dataframe column to list
    address_list = list(df[address])

    #create empty lists to append
    lat_list = []
    long_list = []
    geocode_addr = []

    #loop through address list
    for i in range(len(address_list)):
        #geocode function returns a list of multiple results
        results = geocode(address_list[i])
        #grabs first result from list - most likely match
        result = results[0]
        #get resulting address
        match_addr = result["address"]
        #append address to list
        geocode_addr.append(match_addr)
        #get latitude result and append to latitude list
        lat = result["location"]["y"]
        lat_list.append(lat)
        #get longitude result and append to longitude list
        long = result["location"]["x"]
        long_list.append(long)

    #create new dataframes columns
    df["Latitude"] = lat_list
    df["Longitude"] = long_list
    df["Address_Match"] = geocode_addr

    #create geodataframe
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    #set coordinate system
    gdf.crs = 'epsg:4326'

    print("You have " + str(len(address_list)) + " addresses.")
    print("Addresses downloaded.")

    return gdf

#map points to regions
def region_map(df, core_regions):
    regions = gpd.read_file(core_regions)
    # select only needed columns
    regions = regions[['name', 'slug', 'geometry']]
    # convert lat long file to geodataframe
    locations = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    # set .crs attribute to web mercator projection
    regions.crs = "EPSG:4326"
    locations.crs = "EPSG:4326"
    # spatial join
    mapped_points = gpd.sjoin(locations, regions, how="inner", op="within")
    # create empty file
    download = asksaveasfile(defaultextension=".csv", mode="a")
    # download to the empty file
    mapped_points.to_csv(download.name)
    return mapped_points