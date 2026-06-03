import sqlite3
import os
import datetime
import json

DB_PATH = "storage.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
    except Exception:
        pass
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Contacts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        jid TEXT PRIMARY KEY,
        push_name TEXT,
        profile_pic TEXT,
        notes TEXT,
        tags TEXT, -- JSON string
        is_favorite INTEGER DEFAULT 0,
        is_archived INTEGER DEFAULT 0,
        unread_count INTEGER DEFAULT 0,
        last_message_time TIMESTAMP
    )
    ''')
    
    # Messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        jid TEXT,
        sender TEXT,
        content TEXT,
        type TEXT DEFAULT 'text',
        metadata TEXT, -- JSON string for media URLs, etc.
        timestamp TIMESTAMP,
        from_me INTEGER DEFAULT 0,
        is_read INTEGER DEFAULT 0,
        status TEXT DEFAULT 'sent',
        FOREIGN KEY (jid) REFERENCES contacts (jid)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_group_members (
        group_id INTEGER NOT NULL,
        jid TEXT NOT NULL,
        added_at TIMESTAMP,
        PRIMARY KEY (group_id, jid),
        FOREIGN KEY (group_id) REFERENCES contact_groups (id),
        FOREIGN KEY (jid) REFERENCES contacts (jid)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        is_active INTEGER DEFAULT 0,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flow_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flow_id INTEGER NOT NULL,
        priority INTEGER DEFAULT 100,
        match_type TEXT NOT NULL,
        match_value TEXT,
        action_type TEXT NOT NULL,
        action_value TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (flow_id) REFERENCES flows (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

def save_message(msg_id, jid, sender, content, msg_type='text', metadata=None, from_me=0):
    conn = get_db()
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now()
    metadata_json = json.dumps(metadata) if metadata else None
    
    cursor.execute('''
    INSERT OR REPLACE INTO messages (id, jid, sender, content, type, metadata, timestamp, from_me, is_read)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (msg_id, jid, sender, content, msg_type, metadata_json, timestamp, from_me, 1 if from_me else 0))
    
    # Update contact metadata and increment unread count if not from me
    if not from_me:
        cursor.execute('''
        UPDATE contacts SET last_message_time = ?, unread_count = unread_count + 1 WHERE jid = ?
        ''', (timestamp, jid))
    else:
        cursor.execute('''
        UPDATE contacts SET last_message_time = ? WHERE jid = ?
        ''', (timestamp, jid))
    
    conn.commit()
    conn.close()

def mark_as_read(jid):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET is_read = 1 WHERE jid = ?", (jid,))
    cursor.execute("UPDATE contacts SET unread_count = 0 WHERE jid = ?", (jid,))
    conn.commit()
    conn.close()

def update_contact(jid, push_name=None, notes=None, tags=None, is_favorite=None, is_archived=None, profile_pic=None):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT jid FROM contacts WHERE jid = ?", (jid,))
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute("INSERT INTO contacts (jid, push_name) VALUES (?, ?)", (jid, push_name))
    
    if push_name:
        cursor.execute("UPDATE contacts SET push_name = ? WHERE jid = ?", (push_name, jid))
    if notes is not None:
        cursor.execute("UPDATE contacts SET notes = ? WHERE jid = ?", (notes, jid))
    if tags is not None:
        cursor.execute("UPDATE contacts SET tags = ? WHERE jid = ?", (json.dumps(tags), jid))
    if is_favorite is not None:
        cursor.execute("UPDATE contacts SET is_favorite = ? WHERE jid = ?", (1 if is_favorite else 0, jid))
    if is_archived is not None:
        cursor.execute("UPDATE contacts SET is_archived = ? WHERE jid = ?", (1 if is_archived else 0, jid))
    if profile_pic is not None:
        cursor.execute("UPDATE contacts SET profile_pic = ? WHERE jid = ?", (profile_pic, jid))
        
    conn.commit()
    conn.close()

def get_all_chats():
    conn = get_db()
    cursor = conn.cursor()
    # Get contacts with last message preview
    cursor.execute('''
    SELECT c.*, m.content as last_msg, m.timestamp as last_time
    FROM contacts c
    LEFT JOIN messages m ON m.id = (
        SELECT id FROM messages WHERE jid = c.jid ORDER BY timestamp DESC LIMIT 1
    )
    ORDER BY c.last_message_time DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def _coerce_message_row(row):
    d = dict(row) if row is not None else None
    if not d:
        return d
    md = d.get("metadata")
    if isinstance(md, str) and md:
        try:
            d["metadata"] = json.loads(md)
        except Exception:
            d["metadata"] = {}
    elif md is None:
        d["metadata"] = {}
    return d

def get_chat_history(jid, limit=50):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM messages WHERE jid = ? ORDER BY timestamp ASC LIMIT ?
    ''', (jid, limit))
    rows = cursor.fetchall()
    conn.close()
    return [_coerce_message_row(row) for row in rows]

def get_message_by_id(msg_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE id = ? LIMIT 1", (msg_id,))
    row = cursor.fetchone()
    conn.close()
    return _coerce_message_row(row)

def get_metrics():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM contacts")
    contacts_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages")
    messages_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT jid) FROM messages")
    chats_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "contacts": contacts_count,
        "messages": messages_count,
        "chats": chats_count
    }

def get_all_contacts_from_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts ORDER BY push_name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def list_contact_groups():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM contact_groups ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def create_contact_group(name):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    cursor.execute("INSERT INTO contact_groups (name, created_at) VALUES (?, ?)", (name, now))
    group_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return group_id

def rename_contact_group(group_id, new_name):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE contact_groups SET name = ? WHERE id = ?", (new_name, group_id))
        changed = cursor.rowcount and cursor.rowcount > 0
        conn.commit()
        return bool(changed)
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_contact_group(group_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contact_group_members WHERE group_id = ?", (group_id,))
    cursor.execute("DELETE FROM contact_groups WHERE id = ?", (group_id,))
    conn.commit()
    conn.close()

def add_group_members(group_id, jids):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    added = 0
    for jid in jids:
        if not jid:
            continue
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO contact_group_members (group_id, jid, added_at) VALUES (?, ?, ?)",
                (group_id, jid, now)
            )
            if cursor.rowcount and cursor.rowcount > 0:
                added += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    return added

def get_group_members(group_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.jid, c.push_name
    FROM contact_group_members gm
    JOIN contacts c ON c.jid = gm.jid
    WHERE gm.group_id = ?
    ORDER BY c.push_name ASC
    ''', (group_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def remove_group_members(group_id, jids):
    conn = get_db()
    cursor = conn.cursor()
    removed = 0
    for jid in jids:
        if not jid:
            continue
        try:
            cursor.execute("DELETE FROM contact_group_members WHERE group_id = ? AND jid = ?", (group_id, jid))
            if cursor.rowcount and cursor.rowcount > 0:
                removed += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    return removed

def list_flows():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, is_active, created_at, updated_at FROM flows ORDER BY is_active DESC, name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_active_flow():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, is_active, created_at, updated_at FROM flows WHERE is_active = 1 LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_flow(name, is_active=False):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    cursor.execute(
        "INSERT INTO flows (name, is_active, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (name, 1 if is_active else 0, now, now)
    )
    flow_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return flow_id

def rename_flow(flow_id, new_name):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    try:
        cursor.execute("UPDATE flows SET name = ?, updated_at = ? WHERE id = ?", (new_name, now, flow_id))
        changed = cursor.rowcount and cursor.rowcount > 0
        conn.commit()
        return bool(changed)
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def set_active_flow(flow_id):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    try:
        cursor.execute("UPDATE flows SET is_active = 0, updated_at = ? WHERE is_active = 1", (now,))
        cursor.execute("UPDATE flows SET is_active = 1, updated_at = ? WHERE id = ?", (now, flow_id))
        changed = cursor.rowcount and cursor.rowcount > 0
        conn.commit()
        return bool(changed)
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_flow(flow_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flow_rules WHERE flow_id = ?", (flow_id,))
    cursor.execute("DELETE FROM flows WHERE id = ?", (flow_id,))
    conn.commit()
    conn.close()

def list_flow_rules(flow_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, flow_id, priority, match_type, match_value, action_type, action_value, enabled, created_at, updated_at
        FROM flow_rules
        WHERE flow_id = ?
        ORDER BY priority ASC, id ASC
    """, (flow_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def create_flow_rule(flow_id, priority, match_type, match_value, action_type, action_value, enabled=True):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    cursor.execute("""
        INSERT INTO flow_rules
            (flow_id, priority, match_type, match_value, action_type, action_value, enabled, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (flow_id, int(priority), match_type, match_value, action_type, action_value, 1 if enabled else 0, now, now))
    rule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rule_id

def update_flow_rule(rule_id, priority=None, match_type=None, match_value=None, action_type=None, action_value=None, enabled=None):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    fields = []
    values = []
    if priority is not None:
        fields.append("priority = ?")
        values.append(int(priority))
    if match_type is not None:
        fields.append("match_type = ?")
        values.append(match_type)
    if match_value is not None:
        fields.append("match_value = ?")
        values.append(match_value)
    if action_type is not None:
        fields.append("action_type = ?")
        values.append(action_type)
    if action_value is not None:
        fields.append("action_value = ?")
        values.append(action_value)
    if enabled is not None:
        fields.append("enabled = ?")
        values.append(1 if enabled else 0)
    if not fields:
        conn.close()
        return False
    fields.append("updated_at = ?")
    values.append(now)
    values.append(rule_id)
    try:
        cursor.execute(f"UPDATE flow_rules SET {', '.join(fields)} WHERE id = ?", values)
        changed = cursor.rowcount and cursor.rowcount > 0
        conn.commit()
        return bool(changed)
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_flow_rule(rule_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flow_rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()

def is_message_processed(msg_id):
    """Checks if a message ID has already been processed to prevent double responses."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM messages WHERE id = ?", (msg_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
