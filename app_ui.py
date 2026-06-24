import tkinter as tk
import customtkinter as ctk
import threading
import requests
from database import lookup_member_data, lookup_tariff_rate, log_transaction

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MedAuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("🛡️ MedAuth Pro — Claims Adjudication Portal")
        self.geometry("950(650")
        self.geometry("950x650")
        self.resizable(False, False)

        # Main Layout Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # -------------------------------------------------------------
        # HEADER PANEL
        # -------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#1a365d")
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        self.header_label = ctk.CTkLabel(
            self.header_frame, 
            text="MEDAUTH PRO: ENTERPRISE CLAIMS GATEWAY", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        self.header_label.pack(pady=20, padx=20, anchor="w")

        # -------------------------------------------------------------
        # WORKSPACE PANEL (Split into Left Input and Right Audit)
        # -------------------------------------------------------------
        self.workspace = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
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
            font=ctk.CTkFont(size=11, italic=True),
            text_color="#718096",
            wraplength=260,
            justify="left"
        )
        self.lbl_diagnostic_desc.pack(pady=(0, 15), padx=20, anchor="w")

        # Hospital Provider Menu (Updated to match your seeded options)
        self.lbl_hospital = ctk.CTkLabel(self.form_frame, text="Healthcare Facility Provider:", font=ctk.CTkFont(weight="bold"))
        self.lbl_hospital.pack(pady=(5, 2), padx=20, anchor="w")
        self.opt_hospital = ctk.CTkOptionMenu(
            self.form_frame, 
            values=["The Nairobi Hospital", "The Aga Khan Hospital", "MP Shah Hospital", "Kajiado District Hospital"], 
            width=260
        )
        self.opt_hospital.pack(pady=(0, 15), padx=20, anchor="w")

        # Medical Procedure Menu
        self.lbl_procedure = ctk.CTkLabel(self.form_frame, text="Surgical Procedure Case:", font=ctk.CTkFont(weight="bold"))
        self.lbl_procedure.pack(pady=(5, 2), padx=20, anchor="w")
        self.opt_procedure = ctk.CTkOptionMenu(self.form_frame, values=["Appendectomy", "Cholecystectomy"], width=260)
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

        # --- RIGHT SIDE: LIVE TRANSACTION AUDIT TRAIL ---
        self.audit_frame = ctk.CTkFrame(self.workspace, corner_radius=10)
        self.audit_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        self.lbl_audit = ctk.CTkLabel(self.audit_frame, text="📜 Live Adjudication Audit Trail Log", font=ctk.CTkFont(weight="bold", size=14))
        self.lbl_audit.pack(pady=(15, 10), padx=15, anchor="w")

        self.txt_log = ctk.CTkTextbox(self.audit_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.txt_log.insert("0.0", "SYSTEM STANDBY: Ready to verify medical claims parameters...\n")


    def trigger_nlm_lookup(self):
            """Spawns an isolated background worker thread to pull terms from the US Medical Library."""
            target_code = self.ent_icd.get().strip().upper()
            if not target_code:
                self.lbl_diagnostic_desc.configure(text="❌ Error: Please enter a code first", text_color="#e53e3e")
                return
    
            self.lbl_diagnostic_desc.configure(text="⏳ Accessing National Library of Medicine API...", text_color="#3182ce")
            threading.Thread(target=self._fetch_nlm_api_worker, args=(target_code,), daemon=True).start()    

            def _fetch_nlm_api_worker(self, code):
                    """Asynchronous network handler hitting the official NLM Clinical Table API."""
                    try:
                        url = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms={code}&sf=code,short_desc"
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            data = response.json()
                            if data and len(data) > 3 and data[3]:
                                extracted_description = data[3][0][1]
                                self.after(0, lambda: self.lbl_diagnostic_desc.configure(
                                    text=f"✅ NLM Confirmed: {extracted_description}", 
                                    text_color="#2f855a"
                                ))
                            else:
                                self.after(0, lambda: self.lbl_diagnostic_desc.configure(
                                    text="⚠️ Code not recognized by NLM database", 
                                    text_color="#dd6b20"
                                ))
                        else:
                            self.after(0, lambda: self.lbl_diagnostic_desc.configure(
                                text="❌ Connection issue contacting NLM API", 
                                text_color="#e53e3e"
                            ))
                    except Exception:
                        self.after(0, lambda: self.lbl_diagnostic_desc.configure(
                            text="❌ Offline: Failed to fetch definition data", 
                            text_color="#e53e3e"
                        ))
            
                # -------------------------------------------------------------
                # ADJUDICATION RULES ENGINE INTEGRATOR
                # -------------------------------------------------------------
            def process_adjudication_claim(self):
                    """Coordinates calculations and relational data updates."""
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
            
                    # Fixed function call to match your lookup_member_data function
                    member_row = lookup_member_data(member_id)
                    if not member_row:
                        self.txt_log.insert(tk.END, f"\n❌ ERROR: Member record token '{member_id}' not found in registry.\n")
                        return
            
                    # Parsing using SQLite text Row index mapping
                    patient_name = member_row["name"]
                    policy_name = member_row["policy_tier"]
                    copay_pct = member_row["copay_percent"]
                    remaining_balance = member_row["remaining_balance"]
            
                    # Fixed function call to match your lookup_tariff_rate function
                    contract_cap = lookup_tariff_rate(hospital, procedure)
                    
                    # Default fallback value if procedure isn't specified for that specific facility
                    if contract_cap is None:
                        contract_cap = remaining_balance 
            
                    overcharge_blocked = 0.0
                    allowed_bill = billed_amount
                    if billed_amount > contract_cap:
                        overcharge_blocked = billed_amount - contract_cap
                        allowed_bill = contract_cap
            
                    # Execute split calculations
                    patient_copay_liability = allowed_bill * (copay_pct / 100.0)
                    insurer_net_liability = allowed_bill - patient_copay_liability
            
                    # Simulated live currency exchange tracking parameters
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
            
                    # Balance check evaluation
                    if insurer_net_liability > remaining_balance:
                        status = "DECLINED"
                        self.txt_log.insert(tk.END, "🚨 OUTCOME: CLAIM DECLINED (Insufficient Policy Cap Pool)\n")
                        self.txt_log.insert(tk.END, f"Available Balance remains: KSh {remaining_balance:,.2f}\n")
                    else:
                        status = "AUTO_APPROVED"
                        self.txt_log.insert(tk.END, "🟢 OUTCOME: AUTO_APPROVED\n")
                        self.txt_log.insert(tk.END, "✅ System Ledger written. Letter of Guarantee generated.\n")
            
                    # Fixed call mapping to match your exact 9-argument log_transaction parameters
                    log_transaction(
                        member_id, 
                        hospital, 
                        procedure, 
                        billed_amount,        # proposed_cost
                        allowed_bill,         # allowed_amount
                        overcharge_blocked,   # overcharge_blocked
                        insurer_net_liability,# insurer_liability
                        patient_copay_liability,# patient_copay
                        status                # status
                    )