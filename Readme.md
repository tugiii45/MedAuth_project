#  MedAuth Pro – Intelligent Health Insurance Claims Management System

## Overview

**MedAuth Pro** is a desktop-based health insurance claims management system developed using Python and CustomTkinter. It streamlines the medical claims adjudication process by allowing insurance case managers to verify patient eligibility, estimate procedure costs, validate diagnosis codes, and automatically adjudicate claims based on predefined policy rules.

The system also provides a dedicated patient self-service portal where members can view their insurance benefits, monitor policy utilization, and estimate procedure costs before seeking treatment.



#  Problem Statement

Health insurance claim processing is often slow, manual, and prone to human error. Insurance officers must manually verify:

- Patient eligibility
- Remaining insurance benefits
- Hospital tariff agreements
- Co-payment calculations
- Coverage limits

These manual processes increase processing time and may result in incorrect claim approvals or unnecessary claim rejections.

MedAuth Pro automates these tasks, making claims processing faster, more accurate, and transparent for both insurers and patients.



#  Objectives

The system aims to:

- Automate medical claims adjudication
- Reduce fraudulent or excessive claim approvals
- Improve transparency for insurance members
- Provide instant procedure cost estimates
- Track insurance benefit utilization
- Validate ICD-10 diagnosis codes using the National Library of Medicine (NLM) API

#  Hardcoded Demo Users

| Username | Password |
|----------|----------|
| admin | 1234 | TO ACCESS THE CASE MANAGER DASHBOARD
| conrad | 1234 | TO ACCESS THE CONRAD'S DASHBOARD
| emmanuel | 1234 | TO ACCESS EMMANUEL'S DASHBOARD
| nia | "  " |
| cate | "  " |
| reagan | "  " |

*** NOTE !!! ALL THE USERS HAVE THE SAME PASSWORD ***
# Features

- Secure login for different users
- Member eligibility verification
- ICD-10 diagnostic code lookup using the NLM API
- Procedure cost estimation
- Tariff-based claim adjudication
- Benefit Pulse Tracker
- Automatic co-pay calculation
- Letter of Guarantee (GOP) generation


# Benefit Pulse Tracker

The system visually displays insurance utilization using a progress bar.

### 🟢 Green
Healthy coverage usage.

### 🟡 Yellow
Moderate policy utilization.

### 🔴 Red
Policy nearing annual limit.


# Project Structure

```
MedAuth-Pro/
│
├── database.py
├── login.py
├── case_manager.py
├── patient_dashboard.py
├── nlm_api.py
├── main.py
├── requirements.txt
├── README.md
└── medauth.db
```



#  Installation ( Contributions are highly appreciated )

Clone the repository

```bash
git clone https://github.com/tugiii45/MedAuth_project.git
```

Navigate into the project

```bash
cd MedAuth-Pro
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python main.py
```

#  Developer

**Conrad Karanja**

Health Insurance Claims Management System

Built using Python, SQLite and CustomTkinter.

