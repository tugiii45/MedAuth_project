import tkinter as tk
import customtkinter as ctk
import threading
import requests
from database import lookup_member_data, lookup_tariff_rate, log_transaction

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
