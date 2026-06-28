"""MedAuth application entry point.

Responsibilities:
- Initialize/seed the local SQLite database.
- Launch the UI login gate.

The dashboards (patient/case manager) are opened after successful login.
"""

import sys

import customtkinter as ctk

import database as db
from case_manager import CaseManagerDashboard  # noqa: F401 (kept for import-side registration / clarity)
from login import LoginWindow
from patient_dashboard import PatientDashboard  # noqa: F401


def main() -> None:
    """Start the MedAuth desktop application.

    Workflow:
    1) Initialize the database schema (and seed demo data if needed).
    2) Start the login window.

    If database initialization fails, the app exits with a non-zero code.
    """

    try:
        print("Starting MedAuth System...")
        db.initialize_database()
    except Exception as exc:
        print(f"CRITICAL ERROR: Database initialization failed: {exc}")
        sys.exit(1)

    # Launch the login gate. The window will open the correct dashboard
    # based on the authenticated user's role.
    login = LoginWindow(None)
    login.mainloop()


if __name__ == "__main__":
    main()

