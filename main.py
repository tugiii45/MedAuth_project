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


# Instantiate the UI class from app_ui.py
app = MedAuthApp()
    
    # Start the main Tkinter event loop
app.mainloop()

print("\n==================================================")
print("🛑Application closed safely. Database pipeline disconnected.")

if __name__ == "__main__":
 main()
