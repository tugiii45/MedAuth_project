import sqlite3

DATABASE_NAME = "medauth.db"

def get_db_connection():
    """Establishes a connection to the SQLite database and configures column row access."""
    conn = sqlite3.connect(DATABASE_NAME)
    # Allows fetching database columns by text keys (like row['name']) instead of index tuples
    conn.row_factory = sqlite3.Row
    return conn

