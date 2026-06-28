import tkinter as tk
import customtkinter as ctk
import threading

from tkinter import messagebox

from nlm_api import fetch_icd_description

from database import (
    lookup_member_data,
    lookup_tariff_rate,
    log_transaction,
    estimate_procedure_cost
)


class CaseManagerDashboard(ctk.CTk):

    def __init__(self, logout_callback):
        super().__init__()

        self.logout_callback = logout_callback

        # Window Setup (Fixed layout typo string)
        self.title("🛡️ MedAuth Pro — Claims Adjudication Portal")
        self.geometry("950x720")
        self.resizable(False, False)

        # Main Layout Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # -------------------------------------------------------------
        # HEADER PANEL
        # -------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#1a365d")
        self.header_frame.grid(row=0, column=0, sticky="nsew")

        self.btn_logout = ctk.CTkButton(
        self.header_frame,
        text="Logout",
        width=100,
        fg_color="red",
        hover_color="darkred",
        command=self.logout
)

        self.btn_logout.pack(side="right", padx=20, pady=15)
        self.header_label = ctk.CTkLabel(
            self.header_frame, 
            text="MEDAUTH PRO: ENTERPRISE CLAIMS GATEWAY", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        self.header_label.pack(side="left", padx=20, pady=20)

        # -------------------------------------------------------------
        # WORKSPACE PANEL (Split into Left Input and Right Audit)
        # -------------------------------------------------------------
        self.workspace = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=20, pady=(20, 35))
        self.workspace.grid_columnconfigure(0, weight=4)  # Left form
        self.workspace.grid_columnconfigure(1, weight=5)  # Right log

        # --- LEFT SIDE: ENTRY FORM ---
        self.form_frame = ctk.CTkFrame(self.workspace, corner_radius=10)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        # Member Selection
        self.lbl_member = ctk.CTkLabel(self.form_frame, text="Patient Member ID:", font=ctk.CTkFont(weight="bold"))
        self.lbl_member.pack(pady=(20, 2), padx=20, anchor="w")
        self.ent_member = ctk.CTkEntry(self.form_frame, placeholder_text="e.g., CIG-1001", width=260)
        self.ent_member.pack(pady=(0, 15), padx=20, anchor="w")

        # NLM ICD-10 Diagnostic Code Search
        self.lbl_icd = ctk.CTkLabel(self.form_frame, text="NLM ICD-10 Diagnostic Code:", font=ctk.CTkFont(weight="bold"))
        self.lbl_icd.pack(pady=(5, 2), padx=20, anchor="w")
        
        self.icd_inner_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.icd_inner_frame.pack(pady=(0, 2), padx=20, anchor="w")
        self.ent_icd = ctk.CTkEntry(self.icd_inner_frame, placeholder_text="e.g., K35.8", width=160)
        self.ent_icd.pack(side="left", padx=(0, 10))
        self.btn_nlm = ctk.CTkButton(self.icd_inner_frame, text="Search NLM", width=90, command=self.trigger_nlm_lookup)
        self.btn_nlm.pack(side="left")

        # Live Display for NLM API Description
        self.lbl_diagnostic_desc = ctk.CTkLabel(
            self.form_frame, 
            text="[No verified diagnostic term fetched]", 
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#718096",
            wraplength=260,
            justify="left"
        )
        self.lbl_diagnostic_desc.pack(pady=(0, 15), padx=20, anchor="w")

        # Hospital Provider Menu
        self.lbl_hospital = ctk.CTkLabel(self.form_frame, text="Healthcare Facility Provider:", font=ctk.CTkFont(weight="bold"))
        self.lbl_hospital.pack(pady=(5, 2), padx=20, anchor="w")
        self.opt_hospital = ctk.CTkOptionMenu(
            self.form_frame, 
            values=["The Nairobi Hospital", "The Aga Khan Hospital", "MP Shah Hospital", "Kajiado District Hospital", "Kenyatta National Hospital"], 
            width=260
        )
        self.opt_hospital.pack(pady=(0, 15), padx=20, anchor="w")

        # Medical Procedure Menu
        self.lbl_procedure = ctk.CTkLabel(self.form_frame, text="Surgical Procedure Case:", font=ctk.CTkFont(weight="bold"))
        self.lbl_procedure.pack(pady=(5, 2), padx=20, anchor="w")
        self.opt_procedure = ctk.CTkOptionMenu(self.form_frame, values=["Appendectomy", "Cholecystectomy", "GastroIntestinal",
                "Maternal Procedures",
                "Tonsillectomy"],
                  width=260)
        self.opt_procedure.pack(pady=(0, 15), padx=20, anchor="w")

        # Claim Base Invoice Amount
        self.lbl_bill = ctk.CTkLabel(self.form_frame, text="Gross Invoice Cost (KSh):", font=ctk.CTkFont(weight="bold"))
        self.lbl_bill.pack(pady=(5, 2), padx=20, anchor="w")
        self.ent_bill = ctk.CTkEntry(self.form_frame, placeholder_text="e.g., 100000", width=260)
        self.ent_bill.pack(pady=(0, 25), padx=20, anchor="w")

        # Core Process Call Action
        self.btn_adjudicate = ctk.CTkButton(
            self.form_frame, 
            text="⚡ Run Adjudication Model", 
            height=40, 
            width=260, 
            fg_color="#2b6cb0",
            hover_color="#2b4c7e",
            font=ctk.CTkFont(weight="bold"),
            command=self.process_adjudication_claim
        )
        self.btn_adjudicate.pack(pady=(0, 20), padx=20, anchor="w")

        self.btn_estimate = ctk.CTkButton(
        self.form_frame,
        text="Estimate Cost",
        command=self.estimate_cost
)
        self.btn_estimate.pack(
          fill="x",
          padx=15,
          pady=10
)

        # --- RIGHT SIDE: LIVE TRANSACTION AUDIT TRAIL ---
        self.audit_frame = ctk.CTkFrame(self.workspace, corner_radius=10)
        self.audit_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        self.lbl_audit = ctk.CTkLabel(self.audit_frame, text="📜 Live Adjudication Audit Trail Log", font=ctk.CTkFont(weight="bold", size=14))
        self.lbl_audit.pack(pady=(15, 10), padx=15, anchor="w")

        self.txt_log = ctk.CTkTextbox(self.audit_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.txt_log.insert("0.0", "SYSTEM STANDBY: Ready to verify medical claims parameters...\n")

    # -------------------------------------------------------------
# BENEFIT PULSE TRACKER
# -------------------------------------------------------------
        self.lbl_pulse_title = ctk.CTkLabel(
          self.audit_frame,
          text="📊 Benefit Pulse Tracker",
          font=ctk.CTkFont(weight="bold", size=14)
)
        self.lbl_pulse_title.pack(pady=(10, 5))

        self.pulse_bar = ctk.CTkProgressBar(
           self.audit_frame,
           width=350
)
        self.pulse_bar.pack(pady=5)

        self.pulse_bar.set(0)

        self.lbl_pulse_info = ctk.CTkLabel(
          self.audit_frame,
          text="Coverage utilization will appear here",
          justify="left"
)
        self.lbl_pulse_info.pack(pady=(5, 40))

        


    def _fetch_nlm_api_worker(self, code):
      """
     Background worker for ICD-10 lookups.
      Runs in a separate thread so the UI remains responsive.
     """

      description = fetch_icd_description(code)

      if description:
         self.after(
            0,
            lambda: self.lbl_diagnostic_desc.configure(
                text=f"✅ NLM Confirmed: {description}",
                text_color="#2f855a",
            ),
        )
      else:
        self.after(
            0,
            lambda: self.lbl_diagnostic_desc.configure(
                text="⚠️ Code not recognized by NLM database",
                text_color="#dd6b20",
            ),
        )
    # -------------------------------------------------------------
    # ASYNCHRONOUS BACKEND NETWORK CONTROLLERS
    # -------------------------------------------------------------

    def logout(self):
            self.destroy()              # Close dashboard
            self.logout_callback()      # Open login window    

    
    def trigger_nlm_lookup(self):
        """Start ICD-10 term lookup in a background thread.

        Rationale:
        - The NLM HTTP request can be slow.
        - Running it on a daemon thread keeps the Tkinter UI responsive.
        - UI labels are updated via `self.after(...)` from the worker.
        """
        target_code = self.ent_icd.get().strip().upper()
        if not target_code:
            self.lbl_diagnostic_desc.configure(
                text="❌ Error: Please enter a code first",
                text_color="#e53e3e",
            )
            return

        # Provide immediate feedback while the network call runs.
        self.lbl_diagnostic_desc.configure(
            text="⏳ Accessing National Library of Medicine API...",
            text_color="#3182ce",
        )
        threading.Thread(
            target=self._fetch_nlm_api_worker,
            args=(target_code,),
            daemon=True,
        ).start()

    

    # -------------------------------------------------------------
    # ADJUDICATION RULES ENGINE INTEGRATOR
    # -------------------------------------------------------------
    def process_adjudication_claim(self):
        """Validate inputs, compute liabilities, and write an audit ledger entry.

        High-level flow:
        1) Read UI inputs (member id, facility, procedure, invoice cost).
        2) Validate required fields and ensure invoice cost is numeric.
        3) Load member/policy info from the database.
        4) Load the facility tariff cap for the selected procedure.
           - If no tariff cap exists, fallback to the member's remaining balance.
        5) Cap the billed amount at the tariff cap to compute:
           - allowed_amount
           - overcharge_blocked
        6) Compute patient co-pay and insurer liability.
        7) Decide outcome based on whether insurer liability exceeds the remaining balance.
        8) Log the transaction in `authorization_ledger` (and deduct balance if approved).
        """

        member_id = self.ent_member.get().strip().upper()
        hospital = self.opt_hospital.get()
        procedure = self.opt_procedure.get()
        raw_bill = self.ent_bill.get().strip()


        if not member_id or not raw_bill:
            self.txt_log.insert(tk.END, "\n❌ ERROR: Complete all required form elements.\n")
            return

        try:
            billed_amount = float(raw_bill)
        except ValueError:
            self.txt_log.insert(tk.END, "\n❌ ERROR: Invoice amount must be a numeric value.\n")
            return

        member_row = lookup_member_data(member_id)
        if not member_row:
            self.txt_log.insert(tk.END, f"\n❌ ERROR: Member record token '{member_id}' not found in registry.\n")
            return

        patient_name = member_row["name"]
        policy_name = member_row["policy_tier"]
        copay_pct = member_row["copay_percent"]
        remaining_balance = member_row["remaining_balance"]

        annual_limit = member_row["annual_limit"]

        used_amount = annual_limit - remaining_balance

        utilization = used_amount / annual_limit

        percentage = round(utilization * 100)

        if percentage < 50:
            pulse_status = "🟢 Healthy Coverage"
            pulse_color = "#16a34a"

        elif percentage < 80:
            pulse_status = "🟡 Moderate Utilization"
            pulse_color = "#eab308" 

        else:
            pulse_status = "🔴 Nearing Policy Limit"
            pulse_color = "#dc2626"  

        self.pulse_bar.set(utilization)

        self.pulse_bar.configure(
            progress_color=pulse_color
)     

        self.lbl_pulse_info.configure(
          text=(
            f"{pulse_status}\n"
            f"Annual Limit: KSh {annual_limit:,.2f}\n"
            f"Used Amount: KSh {used_amount:,.2f}\n"
            f"Remaining: KSh {remaining_balance:,.2f}\n"
            f"Utilization: {percentage}%"
    )
)

        contract_cap = lookup_tariff_rate(hospital, procedure)
        
        if contract_cap is None:
            contract_cap = remaining_balance 

        overcharge_blocked = 0.0
        allowed_bill = billed_amount
        if billed_amount > contract_cap:
            overcharge_blocked = billed_amount - contract_cap
            allowed_bill = contract_cap

        patient_copay_liability = allowed_bill * (copay_pct / 100.0)
        insurer_net_liability = allowed_bill - patient_copay_liability

        usd_value = billed_amount / 129.40

        self.txt_log.delete("1.0", tk.END) 
        self.txt_log.insert(tk.END, "=== ADJUDICATION AUDIT TRAIL COMPLETED ===\n\n")
        self.txt_log.insert(tk.END, f"Patient Name : {patient_name}\n")
        self.txt_log.insert(tk.END, f"Policy Tier  : {policy_name} ({copay_pct}% Co-pay Rule)\n")
        self.txt_log.insert(tk.END, f"Gross Invoice: KSh {billed_amount:,.2f} (${usd_value:,.2f} USD)\n")
        self.txt_log.insert(tk.END, f"Tariff Cap   : KSh {contract_cap:,.2f} (Facility Ceiling)\n")
        self.txt_log.insert(tk.END, f"Blocked Over : KSh {overcharge_blocked:,.2f}\n")
        self.txt_log.insert(tk.END, "-----------------------------------------\n")
        self.txt_log.insert(tk.END, f"Insurer Share: KSh {insurer_net_liability:,.2f}\n")
        self.txt_log.insert(tk.END, f"Patient Share: KSh {patient_copay_liability:,.2f}\n\n")

        if insurer_net_liability > remaining_balance:
            status = "DECLINED"
            self.txt_log.insert(tk.END, "🚨 OUTCOME: CLAIM DECLINED (Insufficient Policy Cap Pool)\n")
            self.txt_log.insert(tk.END, f"Available Balance remains: KSh {remaining_balance:,.2f}\n")
        else:
            status = "Approved"
            self.txt_log.insert(tk.END, "🟢 OUTCOME: AUTO_APPROVED\n")
            self.txt_log.insert(tk.END, "✅ System Ledger written. Letter of Guarantee generated.\n")

            self.generate_gop(
              patient_name,
              member_id,
              hospital,
              procedure,
              insurer_net_liability,
              patient_copay_liability
)

        log_transaction(
            member_id, 
            hospital, 
            procedure, 
            billed_amount,        
            allowed_bill,         
            overcharge_blocked,   
            insurer_net_liability,
            patient_copay_liability,
            status                
        )

    def estimate_cost(self):

      member_id = self.ent_member.get().strip().upper()

      hospital_name = self.opt_hospital.get()

      procedure_name = self.opt_procedure.get()

      estimate = estimate_procedure_cost(
        member_id,
        hospital_name,
        procedure_name
    )

      if not estimate:
        messagebox.showerror(
            "Estimator",
            "Unable to generate estimate."
        )
        return

      result = f"""
==========================================
          MEDAUTH COST ESTIMATE
==========================================

🏥 Hospital
{hospital_name}

🩺 Procedure
{procedure_name}

------------------------------------------

💳 Tariff Cap
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

      
    # Create estimate window
      estimate_window = ctk.CTkToplevel(self)
      estimate_window.title("MedAuth Cost Estimate")
      estimate_window.geometry("700x500")
      estimate_window.resizable(True, True)

# Make sure it appears above the dashboard
      estimate_window.lift()
      estimate_window.attributes("-topmost", True)
      estimate_window.after(100, lambda: estimate_window.attributes("-topmost", False))

# Center the window
      estimate_window.update_idletasks()

      width = 700
      height = 500

      screen_width = estimate_window.winfo_screenwidth()
      screen_height = estimate_window.winfo_screenheight()

      x = (screen_width - width) // 2
      y = (screen_height - height) // 2

      estimate_window.geometry(f"{width}x{height}+{x}+{y}")

# Heading
      lbl_title = ctk.CTkLabel(
        estimate_window,
         text="💰 MEDAUTH PROCEDURE COST ESTIMATE",
          font=ctk.CTkFont(size=22, weight="bold")
)
      lbl_title.pack(pady=(20, 10))

# Textbox
      txt_estimate = ctk.CTkTextbox(
       estimate_window,
       font=ctk.CTkFont(size=15)
)
      txt_estimate.pack(fill="both", expand=True, padx=20, pady=10)

      txt_estimate.insert("1.0", result)
      txt_estimate.configure(state="disabled")

# Close button
      btn_close = ctk.CTkButton(
      estimate_window,
    text="Close",
    width=140,
    command=estimate_window.destroy
)
      btn_close.pack(pady=15)
      

    def generate_gop(
      self,
      member_name,
      member_id,
      hospital,
      procedure,
      insurer_amount,
      patient_copay
):

      authorization_id = f"AUTH-{member_id}-{hospital[:3].upper()}"

      gop_text = f"""
========================================
      MEDAUTH LETTER OF GUARANTEE
========================================

Authorization ID:
     {authorization_id}

Patient:
     {member_name}

Member ID:
{member_id}

Hospital:
{hospital}

Procedure:
{procedure}

Approved Amount:
KSh {insurer_amount:,.2f}

Patient Co-Pay:
KSh {patient_copay:,.2f}

Status:
APPROVED

========================================
Generated by MedAuth Pro
========================================
"""
      # Create GOP window
      gop_window = ctk.CTkToplevel(self)
      gop_window.title("Letter of Guarantee")
      gop_window.geometry("700x600")

      txt_gop = ctk.CTkTextbox(
        gop_window,
        font=ctk.CTkFont(size=14)
)
      txt_gop.pack(fill="both", expand=True, padx=20, pady=20)

      txt_gop.insert("1.0", gop_text)
      txt_gop.configure(state="disabled")

      btn_close = ctk.CTkButton(
       gop_window,
       text="Close",
        command=gop_window.destroy
)
      btn_close.pack(pady=15)

      



