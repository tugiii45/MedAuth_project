import requests

# 1. CORE POLICY SCHEMAS
class Policy:
    def __init__(self, policy_tier, annual_limit, copay_percent):
        self.policy_tier = policy_tier
        self.annual_limit = annual_limit
        self.copay_percent = copay_percent

class Member:
    def __init__(self, member_id, name, remaining_balance, policy):
        self.member_id = member_id
        self.name = name
        self.remaining_balance = remaining_balance
        self.policy = policy  # COMPOSITION: Member contains an entire Policy object

# 2. ADJUDICATION TRANSACTION SCHEMAS
class PreAuthRequest:
    def __init__(self, member, hospital_name, procedure, proposed_cost):
        self.member = member
        self.hospital_name = hospital_name
        self.procedure = procedure
        self.proposed_cost = proposed_cost
        
        # Calculation Variables
        self.allowed_amount = 0.0
        self.overcharge_blocked = 0.0
        self.insurer_liability = 0.0
        self.patient_copay = 0.0
        self.status = "PENDING"

    def adjudicate(self, tariff_cap):
        """Processes claims adjudication guidelines."""
        # Check if proposed invoice exceeds contract agreements
        if self.proposed_cost > tariff_cap:
            self.allowed_amount = tariff_cap
            self.overcharge_blocked = self.proposed_cost - tariff_cap
        else:
            self.allowed_amount = self.proposed_cost
            self.overcharge_blocked = 0.0

        # Run Co-pay and Balance Verifications
        copay_fraction = self.member.policy.copay_percent / 100.0
        self.patient_copay = self.allowed_amount * copay_fraction
        self.insurer_liability = self.allowed_amount - self.patient_copay

        if self.allowed_amount <= self.member.remaining_balance:
            self.status = "AUTO_APPROVED"
            return True
        else:
            self.status = "DECLINED_INSUFFICIENT_FUNDS"
            return False

# 3. EXTERNAL DATA STRINGS WEB WORKERS
def fetch_icd_definition(icd_code):
    """Queries the U.S. National Library of Medicine API for clinical definitions."""
    url = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms={icd_code}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data[0] > 0:
                description = data[3][0][1] if isinstance(data[3][0], list) else data[3][0]
                return f"ICD-10 Verified: {description}"
            return "Unknown/Invalid ICD-10 Code Format"
        return "Medical API Lookup Failed (Server Response Error)"
    except Exception:
        return "Medical API Offline (Check internet connection)"

def fetch_live_forex_rate():
    """Queries a public exchange rate API to fetch live USD to KES metrics."""
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data["rates"]["KES"])
        return 129.50
    except Exception:
        return 129.50