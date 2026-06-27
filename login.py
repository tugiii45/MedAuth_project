
import customtkinter as ctk

from database import  get_db_connection
from case_manager import CaseManagerDashboard
from patient_dashboard import PatientDashboard

# Set theme configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    """Secure Gateway access screen (login gate) for the MedAuth desktop UI.

    Notes:
    - This UI collects an operator username and a password PIN.
    - The current implementation performs a direct comparison against the value stored
      in the `users.password_hash` column.
    """

    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success_callback = on_success_callback

        # Window Setup (simple, fixed-size modal-like gate).
        self.title("🛡️ MedAuth Gatekeeper — Authorization Required")
        self.geometry("400x320")
        self.resizable(False, False)

        # Center layout.
        self.grid_columnconfigure(0, weight=1)

        # Header Title.
        self.lbl_title = ctk.CTkLabel(
            self,
            text="MEDAUTH SYSTEM ACCESS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1a365d",
        )
        self.lbl_title.pack(pady=(30, 20))

        # Credentials Fields.
        self.ent_username = ctk.CTkEntry(self, placeholder_text="Username / Operator ID", width=260)
        self.ent_username.pack(pady=10)

        self.ent_password = ctk.CTkEntry(
            self, placeholder_text="Security Password Pin", show="*", width=260
        )
        self.ent_password.pack(pady=10)

        # Interactive Status Feedback Line.
        self.lbl_status = ctk.CTkLabel(
            self, text="Please authenticate to proceed", font=ctk.CTkFont(size=12)
        )
        self.lbl_status.pack(pady=5)

        # Action Execution Trigger.
        self.btn_login = ctk.CTkButton(
            self,
            text="Authenticate Session",
            width=260,
            font=ctk.CTkFont(weight="bold"),
            command=self.verify_credentials,
        )
        self.btn_login.pack(pady=(15, 20))

    def verify_credentials(self):
        """Validate operator credentials against the SQLite `users` table.

        Current behavior:
        - Reads input values from the username and password fields.
        - Queries `users.password_hash` for the provided username.
        - Compares the stored value to the user-entered password.

        Security note:
        - Although the column is named `password_hash`, the current comparison is a
          direct equality check (no hashing performed here). This is documented for
          clarity and may need improvement in a real deployment.
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
            # Query only the password value we need for verification.
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                 """
                 SELECT password_hash, role
                 FROM users
                 WHERE username = ?;
                 """,
                  (username,),
               )
                row = cursor.fetchone()

            # If a record exists, compare stored value to user-entered secret.
            # (See Security note in the docstring.)
            if row and row["password_hash"] == password:

             role = row["role"]

             self.lbl_status.configure(
              text="✅ Verification successful! Loading...",
              text_color="#2f855a"
    )

             self.after(
              600,
               lambda: self.grant_access(role)
    ) 


            else:
                self.lbl_status.configure(
                    text="❌ Invalid operator identification mismatch.",
                    text_color="#e53e3e",
                )
        except Exception:
            # Keep the error generic for UI clarity.
            self.lbl_status.configure(
                text="❌ Database initialization handshake failure.",
                text_color="#e53e3e",
            )

    def grant_access(self, role):

      self.destroy()

      if role == "case_manager":
        app = CaseManagerDashboard(self.show_login)
        app.mainloop()

      elif role == "patient":
       app = PatientDashboard(self.show_login)
       app.mainloop()

    def show_login(self):
      login = LoginWindow(None)
      login.mainloop()