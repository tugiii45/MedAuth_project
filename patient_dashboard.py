import customtkinter as ctk
from tkinter import messagebox

from database import (
    lookup_member_data,
    estimate_procedure_cost
)


class PatientDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("🏥 MedAuth Patient Portal")
        self.geometry("900x600")

        self.header = ctk.CTkLabel(
            self,
            text="PATIENT SELF-SERVICE PORTAL",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.header.pack(pady=20)

        self.lbl_member = ctk.CTkLabel(
            self,
            text="Member ID"
        )
        self.lbl_member.pack()

        self.ent_member = ctk.CTkEntry(
            self,
            width=250
        )
        self.ent_member.pack(pady=10)

        self.lbl_hospital = ctk.CTkLabel(
        self,
        text="Hospital"
)
        self.lbl_hospital.pack()

        self.opt_hospital = ctk.CTkOptionMenu(
        self,
        values=[
        "The Nairobi Hospital",
        "The Aga Khan Hospital",
        "MP Shah Hospital",
        "Kajiado District Hospital"
    ]
)
        self.opt_hospital.pack(pady=10)

        self.lbl_procedure = ctk.CTkLabel(
        self,
        text="Procedure"
)
        self.lbl_procedure.pack()

        self.opt_procedure = ctk.CTkOptionMenu(
        self,
        values=[
        "Appendectomy",
        "Cholecystectomy"
    ]
)
        self.opt_procedure.pack(pady=10)

        self.btn_load = ctk.CTkButton(
            self,
            text="Load My Benefits",
            command=self.load_patient_data
        )
        self.btn_load.pack(pady=10)

        self.btn_estimate = ctk.CTkButton(
        self,
        text="Estimate Procedure Cost",
        command=self.estimate_cost
)
        self.btn_estimate.pack(pady=10)

        self.lbl_estimate_title = ctk.CTkLabel(
        self,
        text="💰 Estimate Summary",
        font=ctk.CTkFont(size=14, weight="bold")
)
        self.lbl_estimate_title.pack(pady=(15, 5))

        self.pulse_bar = ctk.CTkProgressBar(
            self,
            width=400
        )
        self.pulse_bar.pack(pady=20)

        self.txt_estimate = ctk.CTkTextbox(
        self,
        width=450,
        height=140
)
        self.txt_estimate.pack(pady=10)

        self.txt_estimate.insert(
    "1.0",
    "Procedure cost estimate will appear here..."
)

        self.txt_estimate.configure(state="disabled")

        self.lbl_info = ctk.CTkLabel(
            self,
            text="Patient information will appear here"
        )
        self.lbl_info.pack()


    def load_patient_data(self):

      member_id = self.ent_member.get().strip().upper()

      member = lookup_member_data(member_id)

      if not member:
        messagebox.showerror(
            "Error",
            "Member not found"
        )
        return

      annual_limit = member["annual_limit"]

      remaining = member["remaining_balance"]
 
      used = annual_limit - remaining

      utilization = used / annual_limit

      self.pulse_bar.set(utilization)

      self.lbl_info.configure(
        text=(
            f"Name: {member['name']}\n"
            f"Policy: {member['policy_tier']}\n"
            f"Annual Limit: KSh {annual_limit:,.2f}\n"
            f"Remaining Balance: KSh {remaining:,.2f}\n"
            f"Utilization: {round(utilization * 100)}%"
        )
    )

    def estimate_cost(self):

       member_id = self.ent_member.get().strip().upper()

       hospital = self.opt_hospital.get()

       procedure = self.opt_procedure.get()

       estimate = estimate_procedure_cost(
        member_id,
        hospital,
        procedure
    )

       if not estimate:
        messagebox.showerror(
            "Estimate",
            "Unable to calculate the estimate."
        )
        return

       self.txt_estimate.configure(state="normal")

       self.txt_estimate.delete("1.0", "end")

       self.txt_estimate.insert(
    "1.0",
    f"""
       Hospital:
       {hospital}

       Procedure:
       {procedure}

       Tariff Cap:
       KSh {estimate['tariff_cap']:,.2f}

       Insurance Pays:
       KSh {estimate['insurer_liability']:,.2f}

       Patient Co-pay:
       KSh {estimate['patient_copay']:,.2f}
"""
)

       self.txt_estimate.configure(state="disabled")
       