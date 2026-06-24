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