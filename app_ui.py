import tkinter as tk
import customtkinter as ctk
import threading
import requests
from database import lookup_member_data, lookup_tariff_rate, log_transaction, verify_user

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, on_success):
        super().__init__()
        self.title("MedAuth Security")
        self.geometry("320x240")
        self.grab_set()

        ctk.CTkLabel(self, text="System Authentication", font=("Arial", 16, "bold")).pack(pady=20)
        self.ent_user = ctk.CTkEntry(self, placeholder_text="Username")
        self.ent_user.pack(pady=5)
        self.ent_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.ent_pass.pack(pady=5)
        ctk.CTkButton(self, text="Login", command=self.check_login).pack(pady=15)
        self.on_success = on_success

    def check_login(self):
        if verify_user(self.ent_user.get(), self.ent_pass.get()):
            self.on_success()
            self.destroy()
        else:
            self.title("Access Denied!")

class MedAuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🛡️ MedAuth Pro — Claims Adjudication")
        self.geometry("800x500")

        self.label = ctk.CTkLabel(self, text="Member Claims Portal", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.ent_member = ctk.CTkEntry(self, placeholder_text="Enter Member ID")
        self.ent_member.pack(pady=10)

        self.btn_search = ctk.CTkButton(self, text="Lookup Member", command=self.search_member)
        self.btn_search.pack(pady=10)

        self.display = ctk.CTkTextbox(self, width=500, height=150)
        self.display.pack(pady=20)

    def search_member(self):
        m_id = self.ent_member.get()
        data = lookup_member_data(m_id)
        self.display.delete("0.0", "end")
        self.display.insert("0.0", str(data) if data else "Member Not Found.")


    