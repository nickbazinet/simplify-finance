import sqlite3
import pandas as pd
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create buckets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS buckets
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         amount REAL NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    
    # Create expenses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         category TEXT NOT NULL,
         amount REAL NOT NULL,
         date DATE NOT NULL,
         description TEXT)
    ''')
    
    # Create budget table
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         category TEXT NOT NULL,
         amount REAL NOT NULL,
         month DATE NOT NULL)
    ''')
    
    conn.commit()
    conn.close()

# Bucket operations
def add_bucket(name, amount):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO buckets (name, amount) VALUES (?, ?)', (name, amount))
    conn.commit()
    conn.close()

def get_buckets():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM buckets', conn)
    conn.close()
    return df

def update_bucket(bucket_id, amount):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE buckets SET amount = ? WHERE id = ?', (amount, bucket_id))
    conn.commit()
    conn.close()

# Expense operations
def add_expense(category, amount, date, description):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO expenses (category, amount, date, description) VALUES (?, ?, ?, ?)',
              (category, amount, date, description))
    conn.commit()
    conn.close()

def get_expenses(month=None):
    conn = get_db_connection()
    if month:
        df = pd.read_sql_query(
            'SELECT * FROM expenses WHERE strftime("%Y-%m", date) = ?',
            conn,
            params=(month,)
        )
    else:
        df = pd.read_sql_query('SELECT * FROM expenses', conn)
    conn.close()
    return df

# Budget operations
def set_budget(category, amount, month):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO budget (category, amount, month)
        VALUES (?, ?, ?)
    ''', (category, amount, month))
    conn.commit()
    conn.close()

def get_budget(month):
    conn = get_db_connection()
    df = pd.read_sql_query(
        'SELECT * FROM budget WHERE strftime("%Y-%m", month) = ?',
        conn,
        params=(month,)
    )
    conn.close()
    return df

# Initialize database
init_db()
