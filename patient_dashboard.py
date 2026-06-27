import customtkinter as ctk
from tkinter import messagebox


# Import database functions used to retrieve member information
# and estimate procedure costs.
from database import (
    lookup_member_data,
    estimate_procedure_cost
)


# Main Patient Dashboard window
class PatientDashboard(ctk.CTk):

    def __init__(self, logout_callback):
        super().__init__()

        self.logout_callback = logout_callback
    
        # Configure window title and size
        self.title("🏥 MedAuth Patient Portal")
        self.geometry("900x600")

        # Dashboard header
        self.header = ctk.CTkLabel(
            self,
            text="PATIENT SELF-SERVICE PORTAL",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.header.pack(pady=20)

        self.btn_logout = ctk.CTkButton(
        self,
        text="Logout",
        width=100,
        fg_color="red",
        hover_color="darkred",
        command=self.logout
)

        self.btn_logout.place(relx=0.97, y=25, anchor="ne")

        # Member ID label
        self.lbl_member = ctk.CTkLabel(
            self,
            text="INSURANCE CARD ID"
        )
        self.lbl_member.pack()

        # Entry field for the patient to enter their member ID
        self.ent_member = ctk.CTkEntry(
            self,
            width=250
        )
        self.ent_member.pack(pady=10)

        # Hospital selection label
        self.lbl_hospital = ctk.CTkLabel(
        self,
        text="Hospital"
)
        self.lbl_hospital.pack()

        # Dropdown menu containing available hospitals
        self.opt_hospital = ctk.CTkOptionMenu(
        self,
        values=[
        "The Nairobi Hospital",
        "The Aga Khan Hospital",
        "MP Shah Hospital",
        "Kajiado District Hospital",
        "Kenyatta National Hospital"
    ]
)
        self.opt_hospital.pack(pady=10)

        # Procedure selection label
        self.lbl_procedure = ctk.CTkLabel(
        self,
        text="Procedure"
)
        self.lbl_procedure.pack()

        # Dropdown menu containing available medical procedures
        self.opt_procedure = ctk.CTkOptionMenu(
        self,
        values=[
        "Appendectomy",
        "Cholecystectomy",
        "GastroIntestinal",
        "Maternal Procedures",
        "Tonsillectomy"
    ]
)
        self.opt_procedure.pack(pady=10)

        # Button to load the patient's insurance information
        self.btn_load = ctk.CTkButton(
            self,
            text="Load My Benefits",
            command=self.load_patient_data
        )
        self.btn_load.pack(pady=10)

        # Button to estimate the selected procedure cost
        self.btn_estimate = ctk.CTkButton(
        self,
        text="Estimate Procedure Cost",
        command=self.estimate_cost
)
        self.btn_estimate.pack(pady=10)

        # Benefit utilization section
        self.lbl_usage_title = ctk.CTkLabel(
        self,
        text="📊 Insurance Benefit Utilization",
        font=ctk.CTkFont(size=15, weight="bold")
)
        self.lbl_usage_title.pack(pady=(15, 5))

        # Progress bar showing insurance utilization
        self.pulse_bar = ctk.CTkProgressBar(
            self,
            width=400
        )
        self.pulse_bar.pack(pady=20)


        # Displays percentage and benefit summary
        self.lbl_usage = ctk.CTkLabel(
        self,
        text="Benefit usage will appear here.",
        justify="left",
        font=ctk.CTkFont(size=13)
)
        self.lbl_usage.pack(pady=10)

        # Label used to display patient information
        self.lbl_info = ctk.CTkLabel(
            self,
            text="Patient information will appear here"
        )
        self.lbl_info.pack()
    

    # Loads patient details and displays insurance information
    def load_patient_data(self):

      # Retrieve and format the entered member ID
      member_id = self.ent_member.get().strip().upper()

      # Search foself.txtr the member in the database
      member = lookup_member_data(member_id)

      # Display an error if the member does not exist
      if not member:
        messagebox.showerror(
            "Error",
            "Member not found"
        )
        return

      # Retrieve insurance limits and remaining balance
      annual_limit = member["annual_limit"]

      remaining = member["remaining_balance"]

      # Calculate the amount already used
      used = annual_limit - remaining

      # Calculate the percentage utilization
      utilization = used / annual_limit

      # Update the progress bar
      # Update progress bar
      self.pulse_bar.set(utilization)

# Change progress bar color based on utilization
      if utilization < 0.5:
        self.pulse_bar.configure(progress_color="green")
      elif utilization < 0.8:
        self.pulse_bar.configure(progress_color="orange")
      else:
        self.pulse_bar.configure(progress_color="red")

# Display benefit usage details
      self.lbl_usage.configure(
        text=(
        f"Usage: {utilization * 100:.0f}%\n\n"
        f"Annual Limit: KSh {annual_limit:,.2f}\n"
        f"Used: KSh {used:,.2f}\n"
        f"Remaining: KSh {remaining:,.2f}"
    )
)

      # Display the patient's insurance details
      self.lbl_info.configure(
        text=(
            f"Name: {member['name']}\n"
            f"Policy: {member['policy_tier']}\n"
            f"Annual Limit: KSh {annual_limit:,.2f}\n"
            f"Remaining Balance: KSh {remaining:,.2f}\n"
            f"Utilization: {round(utilization * 100)}%"
        )
    )

    # Calculates and displays the estimated procedure cost
    def estimate_cost(self):

       # Retrieve user selections
       member_id = self.ent_member.get().strip().upper()

       hospital = self.opt_hospital.get()

       procedure = self.opt_procedure.get()

       # Request an estimate from the database
       estimate = estimate_procedure_cost(
        member_id,
        hospital,
        procedure
    )

       # Display an error if the estimate cannot be generated
       if not estimate:
        messagebox.showerror(
            "Estimate",
            "Unable to calculate the estimate."
        )
        return

    def logout(self):
       self.destroy()
       self.logout_callback()   

       