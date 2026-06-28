
import customtkinter as ctk

from database import  get_db_connection
from case_manager import CaseManagerDashboard
from patient_dashboard import PatientDashboard

# Set theme configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    """Secure Gateway access screen (login gate) for the MedAuth desktop UI.

    This window authenticates an operator (case manager or patient role) against
    the local SQLite database.

    UI fields:
    - Username / Operator ID
    - Password / PIN

    Notes about security:
    - The schema column is named `password_hash`, but the current implementation
      performs a direct equality comparison (no hashing) for demo purposes.
      This is documented so it is not mistaken for production-grade auth.
    """

    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success_callback = on_success_callback

        # Window setup: small fixed-size gate.
        self.title("🛡️ MedAuth Gatekeeper — Authorization Required")
        self.geometry("400x320")
        self.resizable(False, False)

        # Ensure the layout can expand horizontally if needed.
        self.grid_columnconfigure(0, weight=1)

        # Header.
        self.lbl_title = ctk.CTkLabel(
            self,
            text="MEDAUTH SYSTEM ACCESS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1a365d",
        )
        self.lbl_title.pack(pady=(30, 20))

        # Credentials fields.
        self.ent_username = ctk.CTkEntry(
            self, placeholder_text="Username / Operator ID", width=260
        )
        self.ent_username.pack(pady=10)

        self.ent_password = ctk.CTkEntry(
            self,
            placeholder_text="Security Password Pin",
            show="*",
            width=260,
        )
        self.ent_password.pack(pady=10)

        # Status feedback line.
        self.lbl_status = ctk.CTkLabel(
            self,
            text="Please authenticate to proceed",
            font=ctk.CTkFont(size=12),
        )
        self.lbl_status.pack(pady=5)

        # Login action trigger.
        self.btn_login = ctk.CTkButton(
            self,
            text="Authenticate Session",
            width=260,
            font=ctk.CTkFont(weight="bold"),
            command=self.verify_credentials,
        )
        self.btn_login.pack(pady=(15, 20))

    def verify_credentials(self):
        """Verify entered credentials against SQLite `users`.

        Flow:
        - Validate non-empty input.
        - Query `users` for the given username.
        - Compare stored `password_hash` with the entered PIN (demo logic).
        - On success, route to the dashboard based on stored `role`.
        """

        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()

        # Basic client-side validation to avoid unnecessary DB calls.
        if not username or not password:
            self.lbl_status.configure(
                text="❌ Input fields cannot be empty.", text_color="#e53e3e"
            )
            return

        try:
            # Query only the columns required for verification.
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
             SELECT password_hash, role, member_id
             FROM users
             WHERE username = ?;
             """,
                    (username,),
                )
                row = cursor.fetchone()

            # Compare stored value to user-entered secret.
            if row and row["password_hash"] == password:
                role = row["role"]
                member_id = row["member_id"]

                # Update UI and transition after a short delay.
                self.lbl_status.configure(
                    text="✅ Verification successful! Loading...",
                    text_color="#2f855a",
                )
                self.after(600, lambda: self.grant_access(role, member_id))
            else:
                self.lbl_status.configure(
                    text="❌ Invalid operator identification mismatch.",
                    text_color="#e53e3e",
                )
        except Exception:
            # Keep error message generic to avoid exposing internal errors in UI.
            self.lbl_status.configure(
                text="❌ Database initialization handshake failure.",
                text_color="#e53e3e",
            )

    def grant_access(self, role, member_id):
        """Destroy the login gate and open the dashboard for the authenticated role."""

        self.destroy()

        if role == "case_manager":
            app = CaseManagerDashboard(self.show_login)
            app.mainloop()
        elif role == "patient":
            app = PatientDashboard(member_id, self.show_login)
            app.mainloop()

    def show_login(self):
        """Re-open the login gate (used as a logout callback)."""

        login = LoginWindow(None)
        login.mainloop()
