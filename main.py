import sys
import os


import database as db
from app_ui import MedAuthApp

try:
     db.initialize_database()

except Exception as e:
 print(f"Database Initialization Failed: {e}")
 print("Aborting application startup sequence.")
 sys.exit(1)