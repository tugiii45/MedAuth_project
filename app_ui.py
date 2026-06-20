import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import threading


ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")

class MedAuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()  # Initializes the parent CustomTkinter window setup

        # 1. Main Window Geometry Setup
        self.title("MedAuth Pro — Real-time Insurance Pre-Authorization Engine")
        self.geometry("1100x680")  # Width x Height in pixels
        self.minsize(1000, 600)    # Prevents the user from shrinking the window too small

        # 2. State Variables (App Memory)
        self.current_member = None
        self.current_tariff = None

        # Pull live global baseline rates asynchronously on startup
        self.usd_kes_rate = 129.50  # Initial placeholder fallback rate
        threading.Thread(target=self._async_load_forex, daemon=True).start()

        # 3. Setting up the Window Grid Matrix Layout
        # We divide our window layout into a grid: 2 columns (0 and 1)
        self.grid_columnconfigure(0, weight=1)   # Column 0: Left Sidebar (Narrower)
        self.grid_columnconfigure(1, weight=4)   # Column 1: Right Dashboard Workspace (Wide)
        self.grid_rowconfigure(0, weight=1)      # Row 0 takes up the full vertical height

       
        

    def _async_load_forex(self):
        """Fetches dynamic exchange metrics without freezing the main window main loop thread."""
        rate = mod.fetch_live_forex_rate()  # Calls your models.py API request function
        self.usd_kes_rate = rate
        
        # Safely talk back to the main UI window thread using .after()
        self.after(0, lambda: self.lbl_forex.configure(text=f"Live Forex: 1 USD = {self.usd_kes_rate:.2f} KES"))   

    
    def _build_sidebar(self):
        """Constructs the left-side control panel containing tracking variables and configuration hooks."""
        # A Frame is a structural container box that groups other widgets together
        sidebar = ctk.CTkFrame(self, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        # "nsew" means stretch North, South, East, and West to fill the entire column area
        
        # Branding Header Text (Label)
        lbl_title = ctk.CTkLabel(sidebar, text="📌 MedAuth Pro", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_title.pack(padx=20, pady=(30, 10), anchor="w")  # Pack stacks components sequentially
        
        lbl_subtitle = ctk.CTkLabel(sidebar, text="V1.0.0 Base Build", text_color="gray", font=ctk.CTkFont(size=12))
        lbl_subtitle.pack(padx=20, pady=(0, 30), anchor="w")

        # Network Monitor Inside Box Container
        net_frame = ctk.CTkFrame(sidebar, fg_color=("#EAEAEA", "#2B2B2B"))
        net_frame.pack(padx=15, pady=10, fill="x")
        
        self.lbl_forex = ctk.CTkLabel(net_frame, text="Live Forex: Synchronizing...", font=ctk.CTkFont(size=11))
        self.lbl_forex.pack(padx=10, pady=8, anchor="w")

        # Theme Selector Dropdown Menu
        lbl_theme = ctk.CTkLabel(sidebar, text="Appearance Mode:", font=ctk.CTkFont(size=12))
        lbl_theme.pack(padx=20, pady=(40, 5), anchor="w")
        
        theme_menu = ctk.CTkOptionMenu(sidebar, values=["System", "Dark", "Light"], command=ctk.set_appearance_mode)
        theme_menu.pack(padx=20, pady=5, fill="x")    

    def _build_main_workspace(self):
        """Constructs the right panel featuring clinical input workflows and response matrices."""
        workspace = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        workspace.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        # ================= SECTION 1: IDENTITY ACCESS PANEL =================
        id_group = ctk.CTkFrame(workspace)
        id_group.pack(padx=0, pady=10, fill="x")
        
        lbl_sec1 = ctk.CTkLabel(id_group, text="1. Verify Insured Patient Identity", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_sec1.grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 8), sticky="w")

        # Text input field (Entry Box)
        self.ent_member_id = ctk.CTkEntry(id_group, placeholder_text="Enter Member ID (e.g., CIG-1001)", width=280)
        self.ent_member_id.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

        # Clickable Verification Button linked to a backend function via 'command='
        btn_search_member = ctk.CTkButton(id_group, text="Verify Policy Record", width=140, command=self._action_verify_member)
        btn_search_member.grid(row=1, column=1, padx=5, pady=(0, 15), sticky="w")

        self.lbl_member_summary = ctk.CTkLabel(id_group, text="Status: Awaiting Verification Profile Input...", text_color="gray")
        self.lbl_member_summary.grid(row=1, column=2, padx=20, pady=(0, 15), sticky="w")

        # ================= SECTION 2: ADJUDICATION WORKFLOW ENTRY =================
        adj_group = ctk.CTkFrame(workspace)
        adj_group.pack(padx=0, pady=10, fill="x")

        lbl_sec2 = ctk.CTkLabel(adj_group, text="2. Log Pre-Authorization Claim Request Parameters", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_sec2.grid(row=0, column=0, columnspan=2, padx=15, pady=(12, 8), sticky="w")

        # Dropdown Option Menus
        ctk.CTkLabel(adj_group, text="Facility Name:").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.drop_hospital = ctk.CTkOptionMenu(adj_group, values=["Nairobi Premium Care", "Kajiado District Hospital"], width=280)
        self.drop_hospital.grid(row=1, column=1, padx=15, pady=5, sticky="w")

        ctk.CTkLabel(adj_group, text="Surgical Procedure:").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.drop_procedure = ctk.CTkOptionMenu(adj_group, values=["Appendectomy", "Cholecystectomy"], width=280)
        self.drop_procedure.grid(row=2, column=1, padx=15, pady=5, sticky="w")

        # Pricing and ICD text input slots
        ctk.CTkLabel(adj_group, text="Invoice Proposed Cost (KSh):").grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.ent_cost = ctk.CTkEntry(adj_group, placeholder_text="e.g., 200000", width=280)
        self.ent_cost.grid(row=3, column=1, padx=15, pady=5, sticky="w")

        ctk.CTkLabel(adj_group, text="ICD-10 Diagnostics Code:").grid(row=4, column=0, padx=15, pady=5, sticky="w")
        self.ent_icd = ctk.CTkEntry(adj_group, placeholder_text="e.g., M16.1 or K35.8", width=280)
        self.ent_icd.grid(row=4, column=1, padx=15, pady=5, sticky="w")
        
        self.lbl_icd_status = ctk.CTkLabel(adj_group, text="Clinical Verification: Pending Validation Lookup", text_color="gray", font=ctk.CTkFont(size=12, italic=True))
        self.lbl_icd_status.grid(row=5, column=1, padx=15, pady=(2, 12), sticky="w")

        # Large Evaluation Trigger Button
        self.btn_adjudicate = ctk.CTkButton(adj_group, text="🚀 Evaluate Financial Liability Rules", fill="x", command=self._action_adjudicate_claim)
        self.btn_adjudicate.grid(row=6, column=0, columnspan=2, padx=15, pady=15)

        # ================= SECTION 3: TRANSACTIONAL RESPONSE SCREEN =================
        self.res_group = ctk.CTkFrame(workspace, fg_color=("#F4F4F4", "#202020"))
        self.res_group.pack(padx=0, pady=10, fill="both", expand=True)

        self.lbl_res_status = ctk.CTkLabel(self.res_group, text="AUTOMATED DECISION RADAR OUTCOME: INACTIVE", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        self.lbl_res_status.pack(padx=15, pady=15)

        # Large Multi-line text display block (Textbox)
        self.txt_output_box = ctk.CTkTextbox(self.res_group, height=180, font=ctk.CTkFont(family="Courier", size=13))
        self.txt_output_box.pack(padx=15, pady=(0, 15), fill="x")

        self.btn_gop = ctk.CTkButton(self.res_group, text="Print Official Guarantee of Payment (GOP) Letter", fg_color="green", hover_color="darkgreen", state="disabled", command=self._action_issue_gop)
        self.btn_gop.pack(padx=15, pady=(0, 15), fill="x")

    
    def _action_verify_member(self):
        """Queries relational database row schemas to build active memory objects."""
        m_id = self.ent_member_id.get().strip().upper()  # Extract the text from the entry box
        if not m_id:
            messagebox.showwarning("Validation Warning", "Please enter a valid alphanumeric Member Identification token.")
            return

        row = db.lookup_member_data(m_id)  # Look up data from database.py
        if row:
            # Map database columns directly into memory instances from models.py
            policy_instance = mod.Policy(row['policy_tier'], row['annual_limit'], row['copay_percent'])
            self.current_member = mod.Member(row['member_id'], row['name'], row['remaining_balance'], policy_instance)
            
            # Dynamic Label Customization: Switch text color to green and display verification details
            self.lbl_member_summary.configure(
                text=f"Verified: {self.current_member.name} | Tier: {row['policy_tier']} | Balance: KSh {self.current_member.remaining_balance:,.2f}",
                text_color="green"
            )
        else:
            self.current_member = None
            self.lbl_member_summary.configure(text="Verification Blocked: Insured ID not found in ledger database.", text_color="red")
            messagebox.showerror("Identity Error", f"No record matching active insurance key '{m_id}' exists within database registry files.")        

    def _action_adjudicate_claim(self):
        """Validates entry fields, fires real-time external API streams, and processes ledger analytics."""
        if not self.current_member:
            messagebox.showerror("Process Out of Sequence", "You must perform a successful Member Identity Verification before running transaction rules.")
            return

        icd_code = self.ent_icd.get().strip().upper()
        cost_raw = self.ent_cost.get().strip()

        if not icd_code or not cost_raw:
            messagebox.showwarning("Fields Mismatch", "Surgical transaction costs and diagnostic ICD-10 keys cannot remain blank.")
            return

        try:
            proposed_cost = float(cost_raw)  # Defensive programming conversion check
        except ValueError:
            messagebox.showerror("Data Constraint Mismatch", "Proposed Invoice cost metric parameters must consist strictly of numeric floating structures.")
            return

        # Visual Feedback: Change button status text while fetching web endpoints
        self.btn_adjudicate.configure(state="disabled", text="Connecting to NLM Clinical Registers...")
        self.lbl_icd_status.configure(text="Querying U.S. National Institutes of Health REST endpoints...", text_color="orange")

        # Spawn a background thread worker so the UI window framework doesn't hang!
        def network_thread_worker():
            clinical_description = mod.fetch_icd_definition(icd_code)  # Network fetch line
            
            hosp = self.drop_hospital.get()
            proc = self.drop_procedure.get()
            tariff_cap = db.lookup_tariff_rate(hosp, proc)

            if tariff_cap is None:
                tariff_cap = proposed_cost * 0.90  # Fallback rule safeguard

            claim = mod.PreAuthRequest(self.current_member, hosp, proc, proposed_cost)
            is_approved = claim.adjudicate(tariff_cap)

            # Direct execution back onto the primary display pipeline
            self.after(0, lambda: self._render_adjudication_results(claim, clinical_description, is_approved))

        threading.Thread(target=network_thread_worker, daemon=True).start()

    def _render_adjudication_results(self, claim, clinical_description, is_approved):
        """Updates components across visual fields once internal backend calculation loops resolve."""
        self.btn_adjudicate.configure(state="normal", text="🚀 Evaluate Financial Liability Rules")
        self.lbl_icd_status.configure(text=clinical_description, text_color="green" if "Verified" in clinical_description else "orange")

        self.active_claim = claim
        self.txt_output_box.delete("1.0", tk.END)  # Clear the output text box completely

        # Dynamic Color-Coding States
        if is_approved:
            self.lbl_res_status.configure(text="✅ PRE-AUTHORIZATION CONDITIONALLY APPROVED", text_color="green")
            self.res_group.configure(fg_color=("#EBF7EE", "#142818"))  # Light green vs Dark forest green background
            self.btn_gop.configure(state="normal")
        else:
            self.lbl_res_status.configure(text="❌ PRE-AUTHORIZATION TRANSACTION DECLINED", text_color="red")
            self.res_group.configure(fg_color=("#FDF2F2", "#2D1919"))  # Soft red vs Crimson hue background
            self.btn_gop.configure(state="disabled")

        # Calculate on-the-fly values for global currency representation columns
        usd_cost = claim.proposed_cost / self.usd_kes_rate
        usd_liability = claim.insurer_liability / self.usd_kes_rate

        # Format string dispatch layouts inside the terminal frame widget
        report = (
            f"=== OFFICIAL MEDICAL PRE-AUTH DISPATCH RECORD ===\n"
            f"Patient Name         : {claim.member.name} ({claim.member.member_id})\n"
            f"Medical Provider     : {claim.hospital_name}\n"
            f"Diagnostics Context  : {clinical_description}\n"
            f"Procedure Target     : {claim.procedure}\n\n"
            f"Financial Framework Metrics Breakdown (Local vs Global Framework):\n"
            f"--------------------------------------------------\n"
            f"Submitted Base Cost  : KSh {claim.proposed_cost:,.2f}  (Est: ${usd_cost:,.2f} USD)\n"
            f"Contract Tariff Cap  : KSh {claim.allowed_amount + claim.overcharge_blocked:,.2f}\n"
            f"Inflation Blocked    : KSh {claim.overcharge_blocked:,.2f} <--- Anti-Fraud Savings\n"
            f"--------------------------------------------------\n"
            f"INSURER RUN LIABILITY: KSh {claim.insurer_liability:,.2f}  (Est: ${usd_liability:,.2f} USD)\n"
            f"PATIENT OUT-OF-POCKET: KSh {claim.patient_copay:,.2f}  ({claim.member.policy.copay_percent}% Policy Co-pay)\n"
            f"Lifecycle Status Code: {claim.status}\n"
        )
        self.txt_output_box.insert(tk.END, report)

    def _action_issue_gop(self):
        """Commits final records inside relational ledger databases and deducts member balances."""
        if not hasattr(self, 'active_claim') or not self.active_claim:
            return

        c = self.active_claim
        c.status = "GOP_ISSUED"
        
        # Log the transaction to SQLite via database.py
        db.log_transaction(
            c.member.member_id, c.hospital_name, c.procedure,
            c.proposed_cost, c.allowed_amount, c.overcharge_blocked,
            c.insurer_liability, c.patient_copay, c.status
        )

        messagebox.showinfo("GOP Ledger Success", f"Guarantee of Payment transaction successfully generated and locked into immutable system records! KSh {c.allowed_amount:,.2f} has been deducted from the policy record balance.")
        
        # Refresh the parent display text boxes instantly to show the newly reduced member balances!
        self._action_verify_member()
        self.btn_gop.configure(state="disabled")


if __name__ == "__main__":
    db.initialize_database()  # Pre-verify database structures are ready
    
    