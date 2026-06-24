import sys
import customtkinter as ctk
import database as db
from app_ui import MedAuthApp, LoginWindow

def main():
    # 1. Initialize Database first to ensure data availability
    try:
        print("Starting MedAuth System...")
        db.initialize_database()
    except Exception as e:
        print(f"CRITICAL ERROR: Database initialization failed: {e}")
        sys.exit(1)

    # 2. Define the transition logic
    def start_app():
        
        app = MedAuthApp()
        app.mainloop()

    # 3. Launch Login Window
    login = LoginWindow(start_app)
    login.mainloop()

if __name__ == "__main__":
    main()