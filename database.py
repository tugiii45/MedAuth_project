import sqlite3

DB_NAME = "medauth.db"

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    # Allows fetching rows by column names like a dictionary (e.g., row['name'])
    conn.row_factory = sqlite3.Row  
    return conn


def initialize_users_table():
    """Helper to initialize the Security/Users Table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        );
        """)
        
        # Seed an admin/user if empty (Optional safeguard)
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            # Note: In production, use a library like bcrypt or hashlib for the password
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?);",
                ("admin", "admin_secure_hash", "Administrator")
            )
        conn.commit()


def initialize_database():
    """Creates the structural tables and seeds initial mock data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Enable Foreign Key Constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 2. Create Security/Users Table
        initialize_users_table()

        # 3. Create Policies Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_tier TEXT PRIMARY KEY,
            annual_limit REAL NOT NULL,
            copay_percent REAL NOT NULL
        );
        """)

        # 4. Create Members Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            remaining_balance REAL NOT NULL,
            policy_tier TEXT NOT NULL,
            FOREIGN KEY (policy_tier) REFERENCES policies(policy_tier)
        );
        """)

        # 5. Create Hospital Contract Tariffs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tariffs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_name TEXT NOT NULL,
            procedure_name TEXT NOT NULL,
            tariff_cap REAL NOT NULL,
            UNIQUE(hospital_name, procedure_name)
        );
        """)

        # 6. Create Authorization Transaction Ledger Table
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

        # --- SEEDING MOCK DATA ---
        cursor.execute("SELECT COUNT(*) FROM policies;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("INSERT INTO policies VALUES (?, ?, ?);", [
                ("Corporate Gold", 2500000.0, 10.0),
                ("Retail Silver", 1200000.0, 15.0),
                ("SME Bronze", 600000.0, 20.0)
            ])

            cursor.executemany("INSERT INTO members VALUES (?, ?, ?, ?);", [
                ("CIG-1001", "Conrad Mutugi", 1850000.0, "Corporate Gold"),
                ("CIG-1002", "Cate Sian", 940000.0, "Retail Silver"),
                ("CIG-1003", "Reagan Kendwa", 45000.0, "SME Bronze")
            ])

            cursor.executemany("INSERT INTO tariffs (hospital_name, procedure_name, tariff_cap) VALUES (?, ?, ?);", [
                ("The Nairobi Hospital", "Appendectomy", 150000.0),
                ("The Aga Khan Hospital", "Cholecystectomy", 220000.0),
                ("MP Shah Hospital", "Appendectomy", 85000.0),
                ("Kajiado District Hospital", "Cholecystectomy", 130000.0)
            ])

            conn.commit()
            print("Database initialized and seeded successfully!")
        else:
            print("Database already initialized. Skipping seeding step.")


# --- APP INTERFACE FUNCTIONS ---

def lookup_member_data(member_id):
    """Fetches member and policy details based on member_id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.member_id, m.name, m.remaining_balance, m.policy_tier, p.copay_percent 
            FROM members m
            JOIN policies p ON m.policy_tier = p.policy_tier
            WHERE m.member_id = ?;
        """, (member_id,))
        
        row = cursor.fetchone()
        
    if row:
        return {
            "member_id": row["member_id"],
            "name": row["name"],
            "remaining_balance": row["remaining_balance"],
            "policy_tier": row["policy_tier"],
            "copay_percent": row["copay_percent"]
        }
    return None


def lookup_tariff_rate(hospital_name, procedure_name):
    """Fetches the maximum contract tariff cap for a specific hospital procedure."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tariff_cap 
            FROM tariffs 
            WHERE hospital_name = ? AND procedure_name = ?;
        """, (hospital_name, procedure_name))
        
        row = cursor.fetchone()
        
    return row["tariff_cap"] if row else None


def log_transaction(member_id, hospital_name, procedure_name, proposed_cost, 
                    allowed_amount, overcharge_blocked, insurer_liability, patient_copay, status):
    """Logs the pre-authorization evaluation decision and updates member balances if approved."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Ensure Foreign keys are caught during operations
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute("""
            INSERT INTO authorization_ledger (
                member_id, hospital_name, procedure_name, proposed_cost, 
                allowed_amount, overcharge_blocked, insurer_liability, patient_copay, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (member_id, hospital_name, procedure_name, proposed_cost, 
              allowed_amount, overcharge_blocked, insurer_liability, patient_copay, status))
        
        # Deduct insurer liability from the member's remaining limit if safe & approved
        if status == "Approved":
            cursor.execute("""
                UPDATE members 
                SET remaining_balance = remaining_balance - ? 
                WHERE member_id = ?;
            """, (insurer_liability, member_id))
            
        conn.commit()


if __name__ == "__main__":
    # If run directly, reset/setup the database scheme
    initialize_database()