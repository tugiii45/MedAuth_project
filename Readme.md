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



#  Key Features

##  Case Manager Portal

- Secure login
- Patient member verification
- ICD-10 diagnosis lookup using NLM API
- Hospital selection
- Procedure selection
- Automatic tariff validation
- Co-payment calculation
- Insurance liability calculation
- Claim approval/decline engine
- Automatic audit trail generation
- Benefit Pulse Tracker
- Letter of Guarantee generation
- Procedure cost estimator
- Logout functionality



##  Patient Self-Service Portal

- Secure login
- View insurance information
- View policy type
- Monitor benefit utilization
- Progress bar showing policy usage
- Procedure cost estimation
- Hospital selection
- Procedure selection
- Logout functionality



#  Claims Adjudication Logic

The system automatically:

- Retrieves member information
- Validates policy eligibility
- Checks hospital tariff agreements
- Applies policy co-pay rules
- Calculates insurer liability
- Calculates patient contribution
- Checks remaining policy balance
- Approves or declines claims
- Logs every transaction into the audit database



#  External API Integration

MedAuth Pro integrates with the:

**National Library of Medicine (NLM) Clinical Tables API**

This API is used to:

- Validate ICD-10 diagnosis codes
- Retrieve official disease descriptions
- Improve diagnostic accuracy during claims adjudication



#  Technology Stack

| Technology | Purpose |
|------------|---------|
| Python 3 | Core programming language |
| CustomTkinter | Modern desktop GUI |
| Tkinter | GUI components |
| SQLite | Local database |
| SQL | Database queries |
| Threading | Background API requests |
| REST API | ICD-10 lookup |
| National Library of Medicine API | Diagnosis validation |



#  Database

The application uses SQLite to manage:

- Members
- Insurance policies
- Hospital tariff rates
- Claims history
- Transaction audit logs



#  Hardcoded Demo Users

## Case Manager

| Username | Password |
|----------|----------|
| admin | admin123 |



##  Patient Accounts

Example Member IDs:

```
CIG-1001
CIG-1002
CIG-1003
CIG-1004
```

These IDs can be used to:

- Load insurance information
- Estimate procedure costs
- View benefit utilization


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



#  Installation

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

