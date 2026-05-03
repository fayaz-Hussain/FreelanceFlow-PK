import sqlite3
import json
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/freelanceflow.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            current_rate_usd REAL DEFAULT 0,
            platforms TEXT,
            top_skills TEXT,
            language_pref TEXT DEFAULT 'english',
            past_proposals TEXT,
            last_used_rate REAL,
            total_sessions INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_user(data):
    conn = get_connection()
    cursor = conn.cursor()
    
    user_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    platforms = json.dumps(data.get('platforms', []))
    top_skills = json.dumps(data.get('top_skills', []))
    past_proposals = json.dumps([])
    
    cursor.execute('''
        INSERT INTO users (
            user_id, name, domain, experience_level, current_rate_usd, 
            platforms, top_skills, language_pref, past_proposals, 
            last_used_rate, total_sessions, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data.get('name'),
        data.get('domain'),
        data.get('experience_level'),
        data.get('current_rate_usd', 0),
        platforms,
        top_skills,
        data.get('language_pref', 'english'),
        past_proposals,
        data.get('current_rate_usd', 0),
        0,
        now,
        now
    ))
    
    conn.commit()
    conn.close()
    return user_id

def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        user_dict = dict(row)
        user_dict['platforms'] = json.loads(user_dict['platforms']) if user_dict['platforms'] else []
        user_dict['top_skills'] = json.loads(user_dict['top_skills']) if user_dict['top_skills'] else []
        user_dict['past_proposals'] = json.loads(user_dict['past_proposals']) if user_dict['past_proposals'] else []
        return user_dict
    return None

def update_user(user_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Only update provided fields
    update_fields = []
    update_values = []
    
    for key, value in data.items():
        if key in ['platforms', 'top_skills', 'past_proposals']:
            value = json.dumps(value)
        update_fields.append(f"{key} = ?")
        update_values.append(value)
        
    update_fields.append("updated_at = ?")
    update_values.append(datetime.now().isoformat())
    
    update_values.append(user_id)
    
    query = f'''
        UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?
    '''
    cursor.execute(query, tuple(update_values))
    conn.commit()
    conn.close()

def increment_sessions(user_id):
    user = get_user(user_id)
    if user:
        update_user(user_id, {'total_sessions': user.get('total_sessions', 0) + 1})

def add_proposal(user_id, proposal_text):
    user = get_user(user_id)
    if user:
        proposals = user.get('past_proposals', [])
        proposals.append(proposal_text)
        if len(proposals) > 5:
            proposals = proposals[-5:]
        update_user(user_id, {'past_proposals': proposals})

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name, domain FROM users ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Initialize DB on import
init_db()
