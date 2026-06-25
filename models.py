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
    """Represent a single pre-authorization evaluation request.

    This class encapsulates the core adjudication calculations:
    - apply tariff caps to determine `allowed_amount`
    - split allowed cost into insurer vs patient co-pay liability
    - decide approval based on whether insurer liability fits within remaining balance

    Note: The current UI performs these calculations directly (it doesn't instantiate
    `PreAuthRequest`). This model remains useful as a testable business-logic artifact.
    """

    def __init__(self, member: Member, hospital_name: str, procedure: str, proposed_cost: float):
        self.member = member
        self.hospital_name = hospital_name
        self.procedure = procedure

        # Ensure no negative costs; negative invoices do not make sense here.
        self.proposed_cost = max(0.0, proposed_cost)

        # Output results (computed by `adjudicate`).
        self.allowed_amount = 0.0
        self.overcharge_blocked = 0.0
        self.insurer_liability = 0.0
        self.patient_copay = 0.0
        self.status = "PENDING"

    def adjudicate(self, tariff_cap: Optional[float]) -> bool:
        """Compute allowed amount, split liabilities, and decide approval.

        Args:
            tariff_cap:
                Maximum contract tariff cap for the selected hospital/procedure.
                If `None`, the request is declined because no contract exists.

        Returns:
            True if auto-approved, False if declined.

        Side effects:
            Updates:
            - `allowed_amount`
            - `overcharge_blocked`
            - `patient_copay`
            - `insurer_liability`
            - `status`
        """
        if tariff_cap is None:
            # No tariff contract found for this hospital/procedure.
            self.status = "DECLINED_NO_CONTRACT"
            return False

        # 1) Apply tariff cap.
        #    - `allowed_amount` is what the insurer is willing to cover at most.
        #    - Anything above the cap is blocked/overcharged.
        self.allowed_amount = min(self.proposed_cost, tariff_cap)
        self.overcharge_blocked = self.proposed_cost - self.allowed_amount

        # 2) Split cost into patient co-pay vs insurer liability.
        copay_pct = self.member.policy.copay_percent / 100.0
        self.patient_copay = self.allowed_amount * copay_pct
        self.insurer_liability = self.allowed_amount - self.patient_copay

        # 3) Check funding availability.
        #    - If insurer liability fits within the member's remaining balance pool,
        #      we auto-approve.
        if self.insurer_liability <= self.member.remaining_balance:
            self.status = "AUTO_APPROVED"
            return True

        # Insurer liability exceeds available pool.
        self.status = "DECLINED_INSUFFICIENT_FUNDS"
        return False

    def __repr__(self):
        return f"<PreAuthRequest {self.member.member_id} - {self.status}>"

# --- WEB WORKERS ---
def fetch_icd_definition(icd_code: str) -> str:
    """Query NLM's ICD-10 endpoint and return a human-readable description.

    The current UI uses an inline worker implementation, but this function is
    kept as a reusable “worker-style” helper.

    Args:
        icd_code: ICD-10 CM code string (e.g., "K35.8").

    Returns:
        A short message string, such as:
        - "ICD-10 Verified: <description>"
        - "Invalid ICD-10 Code"
        - "API Error" / "Connection Error"
    """
    url = (
        "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
        f"?terms={icd_code}&sf=code,short_desc"
    )
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