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

    # Create budget table (removed DROP TABLE statement)
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER NOT NULL,
         category TEXT NOT NULL,
         amount REAL NOT NULL,
         UNIQUE(user_id, category),
         FOREIGN KEY (user_id) REFERENCES users (id))
    ''')

    # Create goals table (without current_amount)
    c.execute('''
        CREATE TABLE IF NOT EXISTS goals
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER NOT NULL,
         name TEXT NOT NULL,
         target_amount REAL NOT NULL,
         deadline DATE NOT NULL,
         category TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (user_id) REFERENCES users (id))
    ''')

    # Create goal_buckets table for mapping goals to buckets
    c.execute('''
        CREATE TABLE IF NOT EXISTS goal_buckets
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         goal_id INTEGER NOT NULL,
         bucket_id INTEGER NOT NULL,
         FOREIGN KEY (goal_id) REFERENCES goals (id),
         FOREIGN KEY (bucket_id) REFERENCES buckets (id))
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
def set_budget(user_id, category, amount):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO budget (user_id, category, amount)
        VALUES (?, ?, ?)
    ''', (user_id, category, amount))
    conn.commit()
    conn.close()

def get_budget(user_id):
    conn = get_db_connection()
    df = pd.read_sql_query(
        'SELECT * FROM budget WHERE user_id = ?',
        conn,
        params=(user_id,)
    )
    conn.close()
    return df

def delete_budget(user_id, category):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM budget WHERE user_id = ? AND category = ?', 
              (user_id, category))
    conn.commit()
    conn.close()

# Goal operations
def add_goal(user_id, name, target_amount, deadline, category):
    """Add a new goal and return its ID"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO goals (user_id, name, target_amount, deadline, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, target_amount, deadline, category))
    goal_id = c.lastrowid  # Get the ID of the newly inserted goal
    conn.commit()
    conn.close()
    return goal_id

def get_goals(user_id):
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM goals WHERE user_id = ?', conn, params=(user_id,))
    conn.close()
    return df


def link_goal_to_buckets(goal_id, bucket_ids):
    """Link a goal to selected buckets"""
    conn = get_db_connection()
    c = conn.cursor()
    # Clear existing links
    c.execute('DELETE FROM goal_buckets WHERE goal_id = ?', (goal_id,))
    # Add new links
    for bucket_id in bucket_ids:
        c.execute('INSERT INTO goal_buckets (goal_id, bucket_id) VALUES (?, ?)',
                 (goal_id, bucket_id))
    conn.commit()
    conn.close()

def get_goal_buckets(goal_id):
    """Get buckets linked to a goal"""
    conn = get_db_connection()
    df = pd.read_sql_query('''
        SELECT b.* FROM buckets b
        JOIN goal_buckets gb ON b.id = gb.bucket_id
        WHERE gb.goal_id = ?
    ''', conn, params=(goal_id,))
    conn.close()
    return df

def calculate_goal_current_amount(goal_id):
    """Calculate current amount from linked buckets"""
    buckets_df = get_goal_buckets(goal_id)
    return buckets_df['amount'].sum() if not buckets_df.empty else 0.0

# Initialize database
init_db()