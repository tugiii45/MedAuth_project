import sqlite3

DATABASE_NAME = "medauth.db"

def get_db_connection():
    """Establishes a connection to the SQLite database and configures column row access."""
    conn = sqlite3.connect(DATABASE_NAME)
    # Allows fetching database columns by text keys (like row['name']) instead of index tuples
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    #Creates the structural tables and seeds initial mock data if tables are empty.
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tariffs
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hospital_name TEXT NOT NULL,
                    procedure_name TEXT NOT NULL,
                    tariff_cap REAL NOT NULL,
                    UNIQUE(hospital_name, procedure_name)
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