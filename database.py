import sqlite3

DB_NAME = "medauth.db"


def get_db_connection():
    """Create and return a SQLite connection.

    Notes:
    - Uses `sqlite3.Row` so query results can be accessed by column name, e.g.
      `row['name']`.
    - The connection is meant to be used via a context manager:
        `with get_db_connection() as conn:`
      which auto-commits/rolls back and closes the connection.
    """
    conn = sqlite3.connect(DB_NAME)
    # Enable row-as-dict style access (e.g., row['name']).
    conn.row_factory = sqlite3.Row
    return conn


def initialize_users_table():
    """Create the `users` table and optionally seed an initial admin row.

    The UI expects the following columns:
    - `username`: operator/user identifier (primary key)
    - `password_hash`: stored credential value (currently compared directly)
    - `role`: string label used for future authorization decisions

    Seeding behavior:
    - If the table is empty, an `admin` user is inserted.
    - This is intended for local development/testing.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                member_id TEXT
            );
            """
        )

        # Seed an admin/user if empty (development safeguard).
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            # Security note: In production, store a real salted hash (bcrypt/argon2).
            cursor.executemany(
    """
    INSERT INTO users
    (username, password_hash, role, member_id)
    VALUES (?, ?, ?, ?);
    """,
    [
        ("admin", "1234", "case_manager", None),
        ("conrad", "1234", "patient", "CIG-1001"),
        ("cate", "1234", "patient", "CIG-1002"),
        ("reagan", "1234", "patient", "CIG-1003"),
        ("emmanuel", "1234", "patient", "CIG-1004"),
        ("nia", "1234", "patient", "CIG-1005")
    ]

)
            
        conn.commit()


def initialize_database():
    """Create/upgrade schema and seed initial mock data on first run.

    This function is called by `main.py` before the UI starts.

    Schema overview (local demo):
    - `users`: login/operator credentials for the gate screen
    - `policies`: policy tiers with a co-pay percentage
    - `members`: members tied to a policy tier and a remaining balance pool
    - `tariffs`: hospital/procedure contracted caps (tariff ceiling)
    - `authorization_ledger`: audit log of each adjudication decision

    Seeding behavior:
    - If `policies` is empty, we insert a default set of policies, members, and tariffs.
    - Otherwise, we do not overwrite existing local data.

    Implementation detail:
    - We use `with get_db_connection()` so the connection is properly closed.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1) Enable Foreign Key Constraints for SQLite.
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 2) Users table (login gate).
        initialize_users_table()

        # 3) Policies table (copay percentage by tier).
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS policies (
                policy_tier TEXT PRIMARY KEY,
                annual_limit REAL NOT NULL,
                copay_percent REAL NOT NULL
            );
            """
        )

        # 4) Members table (remaining balance + policy tier FK).
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                remaining_balance REAL NOT NULL,
                policy_tier TEXT NOT NULL,
                FOREIGN KEY (policy_tier) REFERENCES policies(policy_tier)
            );
            """
        )

        # 5) Tariffs (hospital+procedure -> tariff cap).
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tariffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hospital_name TEXT NOT NULL,
                procedure_name TEXT NOT NULL,
                tariff_cap REAL NOT NULL,
                UNIQUE(hospital_name, procedure_name)
            );
            """
        )

        # 6) Ledger (audit trail + balance deduction happens in `log_transaction`).
        cursor.execute(
            """
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
            """
        )

        # --- SEEDING MOCK DATA ---
        cursor.execute("SELECT COUNT(*) FROM policies;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("INSERT INTO policies VALUES (?, ?, ?);", [
                ("Corporate Gold", 2500000.0, 10.0),
                ("Retail Silver", 1200000.0, 15.0),
                ("SME Bronze", 600000.0, 20.0),
            ])

            cursor.executemany("INSERT INTO members VALUES (?, ?, ?, ?);", [
                ("CIG-1001", "Conrad Mutugi", 1850000.0, "Corporate Gold"),
                ("CIG-1002", "Cate Sian", 940000.0, "Retail Silver"),
                ("CIG-1003", "Reagan Kendwa", 500000.0, "SME Bronze"),
                ("CIG-1004", "Emmanuel Opeto", 1000000.0, "Corporate Gold"),
                ("CIG-1005", "Nia Thatiah", 1000000.0, "Retail Silver")

            ])

            cursor.executemany(
                "INSERT INTO tariffs (hospital_name, procedure_name, tariff_cap) VALUES (?, ?, ?);",
                [
                    ("The Nairobi Hospital", "Appendectomy", 150000.0),
                    ("The Aga Khan Hospital", "Cholecystectomy", 220000.0),
                    ("MP Shah Hospital", "Appendectomy", 85000.0),
                    ("Kenyatta National Hospital", "Cholecystectomy", 130000.0),
                    ("The Aga Khan Hospital", "GastroIntestinal", 130000.0),
                    ("MP Shah Hospital", "GastroIntestinal", 140000.0),
                    ("The Nairobi Hospital", "GastroIntestinal", 100000.0),
                    ("The Nairobi Hospital", "Maternal Procedures", 200000.0),
                    ("Kenyatta National Hospital", "GastroIntestinal", 120000.0),
                    ("Kajiado District Hospital", "Maternal Procedures", 100000.0),
                    ("The Aga Khan Hospital", "Maternal Procedures", 250000.0),
                    ("The Nairobi Hospital", "Tonsillectomy", 110000.0),
                    ("Kenyatta National Hospital", "Tonsillectomy", 90000.0),
                    ("The Aga Khan Hospital", "Tonsillectomy", 120000.0),
                    ("Kajiado District Hospital", "Tonsillectomy", 140000.0),
                    ("MP Shah Hospital", "Maternal Procedures", 150000.0),
                    ("Kenyatta National Hospital", "Maternal Procedures", 100000.0),

                
                ],
            )

            conn.commit()
            print("Database initialized and seeded successfully!")
        else:
            print("Database already initialized. Skipping seeding step.")


# --- APP INTERFACE FUNCTIONS ---

def lookup_member_data(member_id):
    """Lookup a member record and its policy attributes.

    Returns:
        dict with keys:
        - member_id
        - name
        - remaining_balance
        - policy_tier
        - copay_percent
        - annual_limit

        or None if the member does not exist.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT m.member_id, m.name, m.remaining_balance,
             m.policy_tier, p.copay_percent,
             p.annual_limit
             FROM members m
             JOIN policies p
                ON m.policy_tier = p.policy_tier
            WHERE m.member_id = ?;
        """, (member_id,))

        row = cursor.fetchone()

    if row:
        return {
    "member_id": row["member_id"],
    "name": row["name"],
    "remaining_balance": row["remaining_balance"],
    "policy_tier": row["policy_tier"],
    "copay_percent": row["copay_percent"],
    "annual_limit": row["annual_limit"]
}

    return None


def lookup_tariff_rate(hospital_name, procedure_name):
    """Fetch the contracted tariff cap for a hospital + procedure.

    Args:
        hospital_name: facility name selected in the UI.
        procedure_name: procedure label selected in the UI.

    Returns:
        float tariff cap if found, otherwise `None`.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tariff_cap 
            FROM tariffs 
            WHERE hospital_name = ? AND procedure_name = ?;
        """, (hospital_name, procedure_name))
        
        row = cursor.fetchone()
        
    return row["tariff_cap"] if row else None


def log_transaction(
    member_id,
    hospital_name,
    procedure_name,
    proposed_cost,
    allowed_amount,
    overcharge_blocked,
    insurer_liability,
    patient_copay,
    status,
):
    """Insert an adjudication record into the ledger and optionally deduct balance.

    Ledger semantics:
    - Always inserts a row into `authorization_ledger` for auditability.
    - If `status == "Approved"`, deducts `insurer_liability` from the member's
      `remaining_balance`.

    Args:
        status: expected values come from the UI (`Approved` / `DECLINED`).
    """
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


def estimate_procedure_cost(
    member_id,
    hospital_name,
    procedure_name
):
    member = lookup_member_data(member_id)

    if not member:
        return None

    tariff_cap = lookup_tariff_rate(
        hospital_name,
        procedure_name
    )

    if tariff_cap is None:
        return None

    copay_percent = member["copay_percent"]

    patient_copay = (
        tariff_cap * copay_percent / 100
    )

    insurer_liability = (
        tariff_cap - patient_copay
    )

    return {
        "tariff_cap": tariff_cap,
        "patient_copay": patient_copay,
        "insurer_liability": insurer_liability
    }

if __name__ == "__main__":
    # If run directly, reset/setup the database scheme
    initialize_database()