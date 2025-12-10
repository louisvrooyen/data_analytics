import geopandas as gpd
import pandas as pd

# Paths to your shapefiles
suburbs_fp = r"D:\Python\DataImports\GeoData\Suburbs.shp"
stations_fp = r"D:\Python\DataImports\GeoData\Fire_Stations.shp"

# Load shapefiles
suburbs = gpd.read_file(suburbs_fp)
stations = gpd.read_file(stations_fp)

# Extract field names (columns)
suburb_fields = list(suburbs.columns)
station_fields = list(stations.columns)

# Build a DataFrame to store them side by side
fields_df = pd.DataFrame({
    "Suburb_Fields": pd.Series(suburb_fields),
    "Station_Fields": pd.Series(station_fields)
})

# Export to CSV
output_fp = r"D:\Python\DataImports\GeoData\Shapefile_FieldNames.csv"
fields_df.to_csv(output_fp, index=False)

print("Field names exported to:", output_fp)