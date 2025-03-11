import sqlite3

def create_database():
    
    # Establish a connection to the database or create it if it doesn't exist
    db_path = "/Users/michaelfortune/Developer/projects/money/money_sql/money.db" 
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Create users table
    cur.execute("""
        CREATE TABLE users (
            username TEXT NOT NULL PRIMARY KEY
        )
    """)
    
    # Create pots table
    cur.execute("""
        CREATE TABLE pots (
            pot_id INTEGER PRIMARY KEY,
            pot_name TEXT NOT NULL,
            start DATE NOT NULL,
            end DATE NOT NULL,
            vault_id INTEGER,
            amount REAL NOT NULL,
            username TEXT NOT NULL,
            FOREIGN KEY (vault_id) REFERENCES vaults(vault_id),
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # Create vaults table
    cur.execute("""
        CREATE TABLE vaults (
            vault_id INTEGER PRIMARY KEY,
            vault_name TEXT NOT NULL,
            start DATE NOT NULL,
            end DATE NOT NULL,
            username TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # Create transactions table
    cur.execute("""
        CREATE TABLE transactions (
            transaction_id INTEGER PRIMARY KEY,
            transaction_name TEXT NOT NULL,
            date DATE NOT NULL,
            pot_id INTEGER,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            username TEXT NOT NULL,
            FOREIGN KEY (pot_id) REFERENCES pots(pot_id),
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # Commit and close the connection 
    con.commit()
    con.close()

    
    
