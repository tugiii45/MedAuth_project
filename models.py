import requests
from typing import Optional

class Policy:
    """Represents an insurance policy tier and its constraints."""
    def __init__(self, policy_tier: str, annual_limit: float, copay_percent: float):
        self.policy_tier = policy_tier
        self.annual_limit = annual_limit
        self.copay_percent = copay_percent

class Member:
    """Represents an insured member with their current balance."""
    def __init__(self, member_id: str, name: str, remaining_balance: float, policy: Policy):
        self.member_id = member_id
        self.name = name
        self.remaining_balance = remaining_balance
        self.policy = policy

class PreAuthRequest:
    """Handles the business logic for claim adjudication."""
    def __init__(self, member: Member, hospital_name: str, procedure: str, proposed_cost: float):
        self.member = member
        self.hospital_name = hospital_name
        self.procedure = procedure
        self.proposed_cost = max(0.0, proposed_cost)  # Ensure no negative costs
        
        # Output results
        self.allowed_amount = 0.0
        self.overcharge_blocked = 0.0
        self.insurer_liability = 0.0
        self.patient_copay = 0.0
        self.status = "PENDING"

    def adjudicate(self, tariff_cap: Optional[float]) -> bool:
        """Processes claims based on pre-negotiated tariff caps."""
        if tariff_cap is None:
            self.status = "DECLINED_NO_CONTRACT"
            return False

        # 1. Check Tariff Caps
        self.allowed_amount = min(self.proposed_cost, tariff_cap)
        self.overcharge_blocked = self.proposed_cost - self.allowed_amount

        # 2. Calculate Liabilities
        copay_pct = self.member.policy.copay_percent / 100.0
        self.patient_copay = self.allowed_amount * copay_pct
        self.insurer_liability = self.allowed_amount - self.patient_copay

        # 3. Check Funding
        if self.insurer_liability <= self.member.remaining_balance:
            self.status = "AUTO_APPROVED"
            return True
        else:
            self.status = "DECLINED_INSUFFICIENT_FUNDS"
            return False

    def __repr__(self):
        return f"<PreAuthRequest {self.member.member_id} - {self.status}>"

# --- WEB WORKERS ---
def fetch_icd_definition(icd_code: str) -> str:
    """Queries the NLM API for clinical definitions."""
    url = f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms={icd_code}&sf=code,short_desc"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 3 and data[3]:
                return f"ICD-10 Verified: {data[3][0][1]}"
            return "Invalid ICD-10 Code"
        return "API Error"
    except Exception:
        return "Connection Error"