# config.py

import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os

# Add GeoData folder to Python path
sys.path.append(r"D:\Python\DataImports\imports")

import config


DB_USER = "root"
DB_PASSWORD = "Qwedcxzao0)16"
DB_HOST = "localhost"
DB_NAME = "incidents"


# Table 1: Full Lookup
TABLE_NAME_streets_lookup_full = "streets_lookup_full"
FILE_PATH_streets_lookup_full = r"D:\OneDriveHome\OneDrive\Documents\Studies\Data Analytics Portfolio\Streets_Suburbs.xlsx"
SHEET_NAME_1 = "Full"

# Table 2: Dictionary Lookup
#TABLE_NAME_2 = "streets_lookup_dictionary"
#FILE_PATH_2 = r"D:\OneDriveHome\OneDrive\Documents\Studies\Data Analytics Portfolio\Streets_Suburbs.xlsx"
#SHEET_NAME_2 = "Limited"

# Expected columns for both tables, Full_Lookup + Dictionary_Lookup
EXPECTED_COLUMNS = [
    "Main_Road", "X_Road", "Latitude", "Longitude", "SUBURB",
    "TOWN", "PROVINCE", "COUNTRY", "Center_Latitude", "Center_Longitude"
]


# Table name 
TABLE_NAME_Fire_Stations = "fire_stations"
FILENAME_fire_stations = r"D:\Python\DataImports\imports\CSV_Files\fire_stations.csv"

#Table Name
TABLE_NAME_Region_Suburb= "region_suburbs"
INPUTFILENAME_REGIONS_SUBURB = "D:\Python\DataImports\CSV_Files\Region_to_Suburb.csv"