import sys
import customtkinter as ctk
import database as db
from app_ui import MedAuthApp, LoginWindow

def start_main_app():
    """Launches the primary Adjudication Portal."""
    app = MedAuthApp()
    app.mainloop()

def main():
    """Orchestrates secure DB initialization and authentication flow."""
    try:
        print("Initializing secure database pipeline...")
        db.initialize_database()
    except Exception as e:
        print(f"CRITICAL ERROR: Database Initialization Failed: {e}")
        print("Aborting application startup sequence.")
        sys.exit(1)

    login = LoginWindow(on_success=start_main_app)
    login.mainloop()