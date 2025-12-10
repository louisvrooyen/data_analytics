import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os

# Add GeoData folder to Python path
sys.path.append(r"D:\Python\DataImports\imports")

import config

print("Loaded config from:", config.__file__)


