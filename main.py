"""MedAuth application entry point.

This file starts the MedAuth application by:
- Setting up the database
- Displaying the login window
- Opening the patient dashboard after a successful login
"""

import sys
import customtkinter as ctk
import database as db
from login import LoginWindow
from case_manager import CaseManagerDashboard
from patient_dashboard import PatientDashboard


# Main function that starts the application
def main():
    """
    Starts the MedAuth desktop application.

    It first prepares the database, then displays
    the login screen. After a successful login,
    the patient dashboard is opened.
    """

    # Initialize the database before launching the application
    try:
        print("Starting MedAuth System...")
        db.initialize_database()

    # Stop the program if the database fails to initialize
    except Exception as e:
        print(f"CRITICAL ERROR: Database initialization failed: {e}")
        sys.exit(1)

    # Function that opens the main dashboard
    # after the user logs in successfully
    def start_app():
         app = PatientDashboard()
         app.mainloop()

    # Create and display the login window
    login = LoginWindow(start_app)
    login.mainloop()


# Run the application only when this file
# is executed directly
if __name__ == "__main__":
    main()