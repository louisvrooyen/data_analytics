import geopandas as gpd

# Paths to your shapefiles
suburbs_fp = r"D:\Python\DataImports\GeoData\Suburbs.shp"
stations_fp = r"D:\Python\DataImports\GeoData\Fire_Stations.shp"

# Load shapefiles
suburbs = gpd.read_file(suburbs_fp)
stations = gpd.read_file(stations_fp)

# Ensure both layers use the same coordinate system
stations = stations.to_crs(suburbs.crs)

# Perform nearest spatial join
suburb_station = gpd.sjoin_nearest(
    suburbs, stations, how="left", distance_col="dist_m"
)

# Keep only relevant fields (adjust names to match your shapefile attributes)
result = suburb_station[["OFC_SBRB_N", "FIRE_STN_N"]]

# Export to CSV
result.to_csv(r"D:\Python\DataImports\GeoData\Suburb_to_FireStation.csv", index=False)

print("Mapping complete! CSV saved to Suburb_to_FireStation.csv")