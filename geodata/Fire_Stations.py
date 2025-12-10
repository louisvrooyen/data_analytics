import geopandas as gpd

# Path to Fire Stations shapefile
stations_fp = r"D:\Python\DataImports\GeoData\Fire_Stations.shp"

# Load shapefile
stations = gpd.read_file(stations_fp)

# Reproject to WGS84 (lat/lon)
stations = stations.to_crs(epsg=4326)

# Extract Lat/Lon with 6 decimal places for MySQL DECIMAL(9,6)
stations["Longitude"] = stations.geometry.x.round(6)
stations["Latitude"] = stations.geometry.y.round(6)

# Convert geometry to WKT (optional, keep for GIS reference)
stations["geometry"] = stations.geometry.apply(lambda g: g.wkt)

# Format column names to Proper Case
stations.columns = [col.title() for col in stations.columns]

# Drop unwanted fields (adjust if needed)
fields_to_drop = ["Address", "Contact_Number"]
stations_clean = stations.drop(columns=[c for c in fields_to_drop if c in stations.columns])

# Export to CSV
output_fp = r"D:\Python\DataImports\GeoData\Fire_Stations_with_geometry_latlon.csv"
stations_clean.to_csv(output_fp, index=False)

print("Export complete! CSV saved with Proper Case fields and DECIMAL(9,6) lat/lon:", output_fp)