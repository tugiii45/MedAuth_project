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

    # Security Entry Point: Initialize the root layer
    root = ctk.CTk()
    root.withdraw()  # Hide the main window while the login screen is active

    # Launch Login Window
    # The 'on_success' lambda destroys the root and triggers the dashboard
    login = LoginWindow(on_success=lambda: (root.destroy(), start_main_app()))
    
    root.mainloop()

    print("\n==================================================")
    print("🛑 Application closed safely. Database pipeline disconnected.")

if __name__ == "__main__":
    main()