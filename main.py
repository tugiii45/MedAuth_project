"""MedAuth application entry-point.

This module is responsible for:
- Initializing the local SQLite database schema (and seeding mock data on first run)
- Showing the login gate
- Launching the main claims adjudication UI after successful authentication
"""

import sys
import customtkinter as ctk
import database as db
from app_ui import MedAuthApp, LoginWindow


def main():
    """Start the MedAuth desktop application.

    The UI requires the database layer, so we initialize it first. If DB setup fails,
    the program terminates early with a clear error message.
    """

    # 1) Initialize database first to ensure member/policy/tariff data is available.
    try:
        print("Starting MedAuth System...")
        db.initialize_database()
    except Exception as e:
        # If schema initialization fails, continuing would cause confusing runtime errors.
        print(f"CRITICAL ERROR: Database initialization failed: {e}")
        sys.exit(1)

    # 2) Define the transition logic.
    # This callback is passed into the login window; on successful auth it will run
    # and show the main application.
    def start_app():
        app = MedAuthApp()
        app.mainloop()

    # 3) Launch the login window (access gate) and block until the user authenticates.
    login = LoginWindow(start_app)
    login.mainloop()


if __name__ == "__main__":
    main()
