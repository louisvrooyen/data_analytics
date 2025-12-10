import geopandas as gpd
import pandas as pd
import os
from shapely.geometry import Polygon, MultiPolygon

# --- Config ---
INPUT_FILE = r"D:\Python\DataImports\CSV_Files\Regions_Suburbs_Nearest.csv"
OUTPUT_FILE = r"D:\Python\DataImports\CSV_Files\Region_to_Suburb.csv"

# --- Step 1: Read input CSV ---
df = pd.read_csv(INPUT_FILE)

# --- Step 2: Convert geometry_wkt column back to GeoSeries ---
# IMPORTANT: Replace EPSG:32735 with the CRS your source data is actually in
gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df["geometry_wkt"]), crs="EPSG:32735")

# --- Step 3: Reproject to EPSG:4326 (WGS84 lat/lon) ---
gdf = gdf.to_crs(epsg=4326)

# --- Step 4: Update geometry_wkt with lat/lon coordinates ---
gdf["geometry_wkt"] = gdf.geometry.apply(lambda g: g.wkt if g is not None else None)

# --- Step 5: Rename columns to match MySQL schema ---
gdf = gdf.rename(columns={
    "OFC_SBRB_N": "Suburb",
    "CITY_HLTH_": "Region",
    "Longitude": "Region_Longitude",
    "Latitude": "Region_Latitude",
    "centroid": "Region_Centroid",
    "Shape__Are_left": "Shape__Are_left",
    "Shape__Len_left": "Shape__Len_left",
    "Shape__Are_right": "Shape__Are_right",
    "Shape__Len_right": "Shape__Len_right"
})

# --- Step 6: Select only required columns ---
selected = gdf[
    [
        "Suburb",
        "Region",
        "Region_Longitude",
        "Region_Latitude",
        "Shape__Are_left",
        "Shape__Len_left",
        "Shape__Are_right",
        "Shape__Len_right",
        "Region_Centroid",
        "geometry_wkt"
    ]
]

# --- Step 7: Validate coordinate ranges ---
invalid_geoms = []
for idx, geom in enumerate(gdf.geometry):
    if geom is None:
        continue
    coords = []
    if isinstance(geom, Polygon):
        coords = geom.exterior.coords
    elif isinstance(geom, MultiPolygon):
        for poly in geom.geoms:
            coords.extend(poly.exterior.coords)

    for x, y in coords:
        if not (-180 <= x <= 180 and -90 <= y <= 90):
            invalid_geoms.append((idx, x, y))

if invalid_geoms:
    print("\n⚠️ Validation Warning: Found geometries with out-of-range coordinates!")
    for idx, x, y in invalid_geoms[:10]:  # show first 10
        print(f" - Row {idx}: ({x}, {y})")
    print("Please check CRS definition in Step 2. These values must be lon/lat degrees.")
else:
    print("\n✅ All geometries validated: coordinates are within lon/lat ranges.")

# --- Step 8: Delete old output if exists ---
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
    print(f"Deleted older export: {OUTPUT_FILE}")

# --- Step 9: Write clean CSV ---
selected.to_csv(OUTPUT_FILE, index=False)
print(f"\nRegion-to-Suburb export written to: {OUTPUT_FILE}")

# --- Step 10: Diagnostics ---
print("\nDiagnostic Summary:")
print(f" - Total suburbs processed: {selected['Suburb'].nunique()}")
print(f" - Total regions matched: {selected['Region'].nunique()}")

region_counts = selected.groupby("Region")["Suburb"].count().sort_values(ascending=False)
print("\nSuburbs per Region:")
for region, count in region_counts.items():
    print(f"   {region}: {count} suburbs")