import sqlite3

DATABASE_NAME = "medauth.db"

def get_db_connection():
    """Establishes a connection to the SQLite database and configures column row access."""
    conn = sqlite3.connect(DATABASE_NAME)
    # Allows fetching database columns by text keys (like row['name']) instead of index tuples
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Creates the structural tables and seeds initial mock data if tables are empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Enable Foreign Key Constraints in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 2. Create Policies Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS policies (
        policy_tier TEXT PRIMARY KEY,
        annual_limit REAL NOT NULL,
        copay_percent REAL NOT NULL
    );
    """)

    # 3. Create Members Table (Links to Policies via Foreign Key)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        member_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        remaining_balance REAL NOT NULL,
        policy_tier TEXT NOT NULL,
        FOREIGN KEY (policy_tier) REFERENCES policies(policy_tier)
    );
    """)

    # 4. Create Hospital Contract Tariffs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tariffs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_name TEXT NOT NULL,
        procedure_name TEXT NOT NULL,
        tariff_cap REAL NOT NULL,
        UNIQUE(hospital_name, procedure_name)
    );
    """)

    # 5. Create Authorization Transaction Ledger Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authorization_ledger (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        procedure_name TEXT NOT NULL,
        proposed_cost REAL NOT NULL,
        allowed_amount REAL NOT NULL,
        overcharge_blocked REAL NOT NULL,
        insurer_liability REAL NOT NULL,
        patient_copay REAL NOT NULL,
        status TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (member_id) REFERENCES members(member_id)
    );
    """)

    # --- SEEDING MOCK DATA FOR THE UI TO QUERY ---
    cursor.execute("SELECT COUNT(*) FROM policies;")
    if cursor.fetchone()[0] == 0:
        # Seed Policy Tiers
        cursor.executemany("""
        INSERT INTO policies (policy_tier, annual_limit, copay_percent)
        VALUES (?, ?, ?);
        """, [
            ("Corporate Gold", 2500000.0, 10.0),   # KSh 2.5M Limit, 10% Copay
            ("Retail Silver", 1200000.0, 15.0),    # KSh 1.2M Limit, 15% Copay
            ("SME Bronze", 600000.0, 20.0)         # KSh 600k Limit, 20% Copay
        ])

        # Seed Member Profiles
        cursor.executemany("""
        INSERT INTO members (member_id, name, remaining_balance, policy_tier)
        VALUES (?, ?, ?, ?);
        """, [
            ("CIG-1001", "Conrad Mutugi", 1850000.0, "Corporate Gold"),
            ("CIG-1002", "Cate Sian", 940000.0, "Retail Silver"),
            ("CIG-1003", "Reagan Kendwa", 45000.0, "SME Bronze")
        ])

        # Seed Pre-Negotiated Hospital Tariff Prices
        cursor.executemany("""
        INSERT INTO tariffs (hospital_name, procedure_name, tariff_cap)
        VALUES (?, ?, ?);
        """, [
            ("The Nairobi Hospital", "Appendectomy", 150000.0),
            ("The Aga Khan Hospital", "Cholecystectomy", 220000.0),
            ("MP Shah Hospital", "Appendectomy", 85000.0),
            ("Kajiado District Hospital", "Cholecystectomy", 130000.0)
        ])

        conn.commit()
        print("Database initialized and seeded successfully!")
    else:
        print("Database already initialized. Skipping seeding step.")

    conn.close()


def lookup_member_data(member_id):
    """Fetches a member joined with their specific policy tier settings."""
    conn = get_db_connection()
    cursor = conn.cursor()

     #JOIN Query
    cursor.execute(""" 
        SELECT m.member_id, m.name, m.remaining_balance, p.policy_tier, p.annual_limit, p.copay_percent
        FROM members m
        JOIN policies p ON m.policy_tier = p.policy_tier
        WHERE m.member_id = ?;
    """, (member_id,))

    row = cursor.fetchone()
    conn.close()
    return row

def lookup_tariff_rate(hospital_name, procedure_name):
    """Fetches the pre-negotiated legal price ceiling for a procedure at a hospital."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tariff_cap FROM tariffs 
        WHERE hospital_name = ? AND procedure_name = ?;
    """, (hospital_name, procedure_name))
    row = cursor.fetchone()
    conn.close()
    return row['tariff_cap'] if row else None

def log_transaction(member_id, hospital, procedure, proposed, allowed, blocked, insurer, patient, status):
    """Commits an immutable record into the authorization transaction ledger."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO authorization_ledger 
        (member_id, hospital_name, procedure_name, proposed_cost, allowed_amount, overcharge_blocked, insurer_liability, patient_copay, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (member_id, hospital, procedure, proposed, allowed, blocked, insurer, patient, status))

    # If claim was approved or issued a GOP, deduct the used insurance pool balance from the member
    if "APPROVED" in status or "GOP" in status:
        cursor.execute("""
            UPDATE members 
            SET remaining_balance = remaining_balance - ? 
            WHERE member_id = ?;
        """, (allowed, member_id))

        conn.commit()
    conn.close()

    
initialize_database()