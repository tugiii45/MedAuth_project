import customtkinter as ctk
from tkinter import messagebox

from database import lookup_member_data


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

        self.btn_load = ctk.CTkButton(
            self,
            text="Load My Benefits",
            command=self.load_patient_data
        )
        self.btn_load.pack(pady=10)

        self.pulse_bar = ctk.CTkProgressBar(
            self,
            width=400
        )
        self.pulse_bar.pack(pady=20)

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