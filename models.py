import threading
import requests

class Policy: #Represents an insurance policy tier detailing coverage rules.

    def __init__(self, tier_name, annual_limit, copay_percent):
        self.tier_name = tier_name
        self.annual_limit = float(annual_limit)
        self.copay_percent = float(copay_percent)

class Member: #Represents an insured client.

    def __init__(self, member_id, name, remaining_balance, policy_obj):
        self.member_id = member_id
        self.name = name
        self.remaining_balance = float(remaining_balance)
        self.policy_obj = policy_obj # Composition: Member HAS A Policy

class PreAuthRequest:
 
    #The core operational entity. Manages checking insurance coverage, applying contracted tariffs, and calculating financial liabilities.
        
    def __init__(self, member_obj, hospital_name, procedure, proposed_cost):
        self.member = member_obj
        self.hospital_name = hospital_name
        self.procedure = procedure
        self.proposed_cost = float(proposed_cost)

        self.allowed_amount = 0.0
        self.overcharge_blocked = 0.0
        self.insurer_liability = 0.0
        self.patient_copay = 0.0
        self.status = "PENDING"


     #Anti-fraud filter called tariff adjudication
    def adjudicate(self, tariff_rate):
        if self.proposed_cost > tariff_rate:
            self.allowed_amount = tariff_rate
            self.overcharge_blocked = self.proposed_cost - tariff_rate
        else:
            self.allowed_amount = self.proposed_cost
            self.overcharge_blocked = 0.0

        if self.allowed_amount > self.member.remaining_balance:
            self.allowed_amount = self.member.remaining_balance
            self.status = "DECLINED_EXCEEDED_LIMITS"
            return False


        copay_fraction = self.member.policy.copay_percent / 100.0
        self.patient_copay = self.allowed_amount * copay_fraction
        self.insurer_liability = self.allowed_amount - self.patient_copay
        self.status = "APPROVED_PENDING_GOP"
        return True


    
    def fetch_icd_definition(icd_code):             

       url = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms={icd_code}" 
       try:
           response = requests.get(url, timeout=5)
           if response.status_with == 200:
            data = response.json()
            # The API returns data structured as: [total_results, codes_list, extra_data, descriptions_list]
            if data[0] > 0:
                description = data[3][0][1] if isinstance(data[3][0], list) else data[3][0]
                return f"ICD-10 Verified: {description}"
            return "Unknown/Invalid ICD-10 Code Format"
            return "Medical API Lookup Failed (Server Response Error)"
       except Exception:
        return "Medical API Offline (Check internet connection)"

    def fetch_live_forex_rate():
    
    #Queries a public currency exchange API to fetch the current USD/KES global baseline rate.
    
    # Using a reliable, unauthenticated public API fallback endpoint
     url = "https://open.er-api.com/v6/latest/USD"
     try:
      response = requests.get(url, timeout=5)
      if response.status_code == 200:
            data = response.json()
            kes_rate = data["rates"].get("KES", 129.50)  # Standard baseline fallback if missing
            return float(kes_rate)
            return 129.50
     except Exception:
      return 129.50  # Default safe hardcoded exchange rate if the user is offline