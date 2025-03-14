import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

def get_db_connection():
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT UNIQUE NOT NULL,
         password_hash TEXT NOT NULL,
         email TEXT UNIQUE NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')

    # Create buckets table with user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS buckets
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER NOT NULL,
         name TEXT NOT NULL,
         amount REAL NOT NULL,
         type TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (user_id) REFERENCES users (id))
    ''')

    # Create expenses table with user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER NOT NULL,
         category TEXT NOT NULL,
         amount REAL NOT NULL,
         date DATE NOT NULL,
         description TEXT,
         FOREIGN KEY (user_id) REFERENCES users (id))
    ''')

    # Create budget table with user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER NOT NULL,
         category TEXT NOT NULL,
         amount REAL NOT NULL,
         month DATE NOT NULL,
         FOREIGN KEY (user_id) REFERENCES users (id))
    ''')

    conn.commit()
    conn.close()

# User operations
def create_user(username, password, email):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute(
            'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
            (username, hash_password(password), email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, username FROM users WHERE username = ? AND password_hash = ?',
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

# Bucket operations
def add_bucket(user_id, name, amount, bucket_type):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO buckets (user_id, name, amount, type) VALUES (?, ?, ?, ?)', 
              (user_id, name, amount, bucket_type))
    conn.commit()
    conn.close()

def get_buckets(user_id):
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM buckets WHERE user_id = ?', conn, params=(user_id,))
    conn.close()
    return df

def update_bucket(bucket_id, amount, user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE buckets SET amount = ? WHERE id = ? AND user_id = ?', 
              (amount, bucket_id, user_id))
    conn.commit()
    conn.close()

# Expense operations
def add_expense(user_id, category, amount, date, description):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO expenses (user_id, category, amount, date, description) VALUES (?, ?, ?, ?, ?)',
              (user_id, category, amount, date, description))
    conn.commit()
    conn.close()

def get_expenses(user_id, month=None):
    conn = get_db_connection()
    if month:
        df = pd.read_sql_query(
            'SELECT * FROM expenses WHERE user_id = ? AND strftime("%Y-%m", date) = ?',
            conn,
            params=(user_id, month)
        )
    else:
        df = pd.read_sql_query('SELECT * FROM expenses WHERE user_id = ?', conn, params=(user_id,))
    conn.close()
    return df

# Budget operations
def set_budget(user_id, category, amount, month):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO budget (user_id, category, amount, month)
        VALUES (?, ?, ?, ?)
    ''', (user_id, category, amount, month))
    conn.commit()
    conn.close()

def get_budget(user_id, month):
    conn = get_db_connection()
    df = pd.read_sql_query(
        'SELECT * FROM budget WHERE user_id = ? AND strftime("%Y-%m", month) = ?',
        conn,
        params=(user_id, month)
    )
    conn.close()
    return df

# Initialize database
init_db()