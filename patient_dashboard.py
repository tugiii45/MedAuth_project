import customtkinter as ctk
from tkinter import messagebox

from database import estimate_procedure_cost, lookup_member_data


class PatientDashboard(ctk.CTk):
    """Patient self-service dashboard.

    Allows a logged-in member to:
    - View remaining benefit utilization (progress bar).
    - Estimate procedure costs using tariff caps and co-pay rules.
    """

    def __init__(self, member_id: str, logout_callback):
        super().__init__()

        # Session context
        self.member_id = member_id
        self.logout_callback = logout_callback

        # Window configuration
        self.title("🏥 MedAuth Patient Portal")
        self.geometry("900x720")

        # Header
        self.header = ctk.CTkLabel(
            self,
            text="PATIENT SELF-SERVICE PORTAL",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.header.pack(pady=20)

        # Logout button (top-right)
        self.btn_logout = ctk.CTkButton(
            self,
            text="Logout",
            width=100,
            fg_color="red",
            hover_color="darkred",
            command=self.logout,
        )
        self.btn_logout.place(relx=0.97, y=25, anchor="ne")

        # Hospital selection
        self.lbl_hospital = ctk.CTkLabel(self, text="Hospital")
        self.lbl_hospital.pack()
        self.opt_hospital = ctk.CTkOptionMenu(
            self,
            values=[
                "The Nairobi Hospital",
                "The Aga Khan Hospital",
                "MP Shah Hospital",
                "Kajiado District Hospital",
                "Kenyatta National Hospital",
            ],
        )
        self.opt_hospital.pack(pady=10)

        # Procedure selection
        self.lbl_procedure = ctk.CTkLabel(self, text="Procedure")
        self.lbl_procedure.pack()
        self.opt_procedure = ctk.CTkOptionMenu(
            self,
            values=[
                "Appendectomy",
                "Cholecystectomy",
                "GastroIntestinal",
                "Maternal Procedures",
                "Tonsillectomy",
            ],
        )
        self.opt_procedure.pack(pady=10)

        # Load benefits button
        self.btn_load = ctk.CTkButton(
            self,
            text="Load My Benefits",
            command=self.load_patient_data,
        )
        self.btn_load.pack(pady=10)

        # Estimate cost button
        self.btn_estimate = ctk.CTkButton(
            self,
            text="Estimate Procedure Cost",
            command=self.estimate_cost,
        )
        self.btn_estimate.pack(pady=10)

        # Benefit utilization section
        self.lbl_usage_title = ctk.CTkLabel(
            self,
            text="📊 Insurance Benefit Utilization",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.lbl_usage_title.pack(pady=(15, 5))

        self.pulse_bar = ctk.CTkProgressBar(self, width=400)
        self.pulse_bar.pack(pady=10)

        # Utilization details text
        self.lbl_usage = ctk.CTkLabel(
            self,
            text="Benefit usage will appear here.",
            justify="left",
            font=ctk.CTkFont(size=13),
        )
        self.lbl_usage.pack(pady=5)

        # Patient information text
        self.lbl_info = ctk.CTkLabel(
            self,
            text="Patient information will appear here",
        )
        self.lbl_info.pack(pady=(15, 25))

    def load_patient_data(self):
        """Load the member record and update utilization UI."""

        member = lookup_member_data(self.member_id)
        if not member:
            messagebox.showerror("Error", "Member not found")
            return

        annual_limit = member["annual_limit"]
        remaining = member["remaining_balance"]
        used = annual_limit - remaining

        # Guard against division by zero in case of malformed demo data.
        utilization = (used / annual_limit) if annual_limit else 0.0

        # Progress bar
        self.pulse_bar.set(utilization)

        # Progress color based on utilization thresholds
        if utilization < 0.5:
            self.pulse_bar.configure(progress_color="green")
        elif utilization < 0.8:
            self.pulse_bar.configure(progress_color="orange")
        else:
            self.pulse_bar.configure(progress_color="red")

        # Summary lines
        self.lbl_usage.configure(
            text=(
                f"Usage: {utilization * 100:.0f}%\n\n"
                f"Annual Limit: KSh {annual_limit:,.2f}\n"
                f"Used: KSh {used:,.2f}\n"
                f"Remaining: KSh {remaining:,.2f}"
            )
        )

        # Patient info
        self.lbl_info.configure(
            text=(
                f"Name: {member['name']}\n"
                f"Policy: {member['policy_tier']}\n"
            )
        )

    def estimate_cost(self):
        """Calculate and display an estimated procedure cost for selected options."""

        hospital = self.opt_hospital.get()
        procedure = self.opt_procedure.get()

        estimate = estimate_procedure_cost(self.member_id, hospital, procedure)
        if not estimate:
            messagebox.showerror("Estimate", "Unable to calculate the estimate.")
            return

        result = f"""
==========================================
          MEDAUTH COST ESTIMATE
==========================================

🏥 Hospital
{hospital}

🩺 Procedure
{procedure}

------------------------------------------

💳 Maximum allowable charge
KSh {estimate['tariff_cap']:,.2f}

🏥 Insurance Pays
KSh {estimate['insurer_liability']:,.2f}

👤 Patient Co-pay
KSh {estimate['patient_copay']:,.2f}

==========================================
This is an estimate based on the selected
hospital, procedure and policy benefits.
==========================================
"""

        # Render result in a pop-up window
        estimate_window = ctk.CTkToplevel(self)
        estimate_window.title("MedAuth Cost Estimate")
        estimate_window.geometry("700x500")

        lbl_title = ctk.CTkLabel(
            estimate_window,
            text="💰 MEDAUTH PROCEDURE COST ESTIMATE",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        lbl_title.pack(pady=(20, 10))

        txt_estimate = ctk.CTkTextbox(
            estimate_window,
            font=ctk.CTkFont(size=15),
        )
        txt_estimate.pack(fill="both", expand=True, padx=20, pady=10)

        txt_estimate.insert("1.0", result)
        txt_estimate.configure(state="disabled")

        btn_close = ctk.CTkButton(
            estimate_window,
            text="Close",
            width=140,
            command=estimate_window.destroy,
        )
        btn_close.pack(pady=15)

    def logout(self):
        """Close this window and route back to the login gate."""

        self.destroy()
        self.logout_callback()

