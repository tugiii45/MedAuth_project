import sys
import customtkinter as ctk
import database as db
from app_ui import MedAuthApp, LoginWindow

def start_main_app():
    """Destroys the login window and initializes the main portal."""
    app = MedAuthApp()
    app.mainloop()

def main():
    try:
        print("Initializing secure database pipeline...")
        db.initialize_database()
    except Exception as e:
        print(f"CRITICAL ERROR: Database Initialization Failed: {e}")
        sys.exit(1)

    # Launch the Login Window as the main entry point
    # We pass the start_main_app function as the success callback
    login = LoginWindow(on_success=lambda: (login.destroy(), start_main_app()))
    login.mainloop()

if __name__ == "__main__":
    main()