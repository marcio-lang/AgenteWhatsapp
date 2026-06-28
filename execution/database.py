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
    
    # New tables for multi-atendimento
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT, -- 'admin' or 'agent'
        status TEXT DEFAULT 'offline'
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        token TEXT,
        status TEXT DEFAULT 'close'
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agent_instances (
        agent_id INTEGER,
        instance_id INTEGER,
        PRIMARY KEY (agent_id, instance_id),
        FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
        FOREIGN KEY (instance_id) REFERENCES instances(id) ON DELETE CASCADE
    )
    ''')
    
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
        last_message_time TIMESTAMP,
        assigned_to INTEGER,
        instance_id INTEGER,
        FOREIGN KEY (assigned_to) REFERENCES agents(id) ON DELETE SET NULL,
        FOREIGN KEY (instance_id) REFERENCES instances(id) ON DELETE CASCADE
    )
    ''')
    
    try:
        cursor.execute("ALTER TABLE contacts ADD COLUMN assigned_to INTEGER;")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE contacts ADD COLUMN instance_id INTEGER;")
    except Exception:
        pass
    
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
        instance_id INTEGER,
        is_internal INTEGER DEFAULT 0,
        FOREIGN KEY (jid) REFERENCES contacts (jid),
        FOREIGN KEY (instance_id) REFERENCES instances(id) ON DELETE CASCADE
    )
    ''')
    
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN instance_id INTEGER;")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN is_internal INTEGER DEFAULT 0;")
    except Exception:
        pass

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

def save_message(msg_id, jid, sender, content, msg_type='text', metadata=None, from_me=0, instance_id=None, is_internal=0):
    conn = get_db()
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now()
    metadata_json = json.dumps(metadata) if metadata else None
    
    cursor.execute('''
    INSERT OR REPLACE INTO messages (id, jid, sender, content, type, metadata, timestamp, from_me, is_read, instance_id, is_internal)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (msg_id, jid, sender, content, msg_type, metadata_json, timestamp, from_me, 1 if from_me else 0, instance_id, is_internal))
    
    # Update contact metadata and increment unread count if not from me and not internal
    if not is_internal:
        if not from_me:
            cursor.execute('''
            UPDATE contacts SET last_message_time = ?, unread_count = unread_count + 1 WHERE jid = ?
            ''', (timestamp, jid))
        else:
            cursor.execute('''
            UPDATE contacts SET last_message_time = ? WHERE jid = ?
            ''', (timestamp, jid))
            
    if instance_id is not None:
        cursor.execute("UPDATE contacts SET instance_id = ? WHERE jid = ?", (instance_id, jid))
    
    conn.commit()
    conn.close()

def mark_as_read(jid):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET is_read = 1 WHERE jid = ?", (jid,))
    cursor.execute("UPDATE contacts SET unread_count = 0 WHERE jid = ?", (jid,))
    conn.commit()
    conn.close()

def update_contact(jid, push_name=None, notes=None, tags=None, is_favorite=None, is_archived=None, profile_pic=None, assigned_to=None, instance_id=None):
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
    if assigned_to is not None:
        if assigned_to in ["unassigned", "", 0, -1, None]:
            cursor.execute("UPDATE contacts SET assigned_to = NULL WHERE jid = ?", (jid,))
        else:
            cursor.execute("UPDATE contacts SET assigned_to = ? WHERE jid = ?", (assigned_to, jid))
    if instance_id is not None:
        cursor.execute("UPDATE contacts SET instance_id = ? WHERE jid = ?", (instance_id, jid))
        
    conn.commit()
    conn.close()

def get_all_chats(instance_id=None, agent_id=None, show_unassigned=True):
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
    SELECT c.*, m.content as last_msg, m.timestamp as last_time
    FROM contacts c
    LEFT JOIN messages m ON m.id = (
        SELECT id FROM messages WHERE jid = c.jid ORDER BY timestamp DESC LIMIT 1
    )
    '''
    
    conditions = []
    params = []
    
    if instance_id is not None:
        conditions.append("c.instance_id = ?")
        params.append(instance_id)
        
    if agent_id is not None:
        if show_unassigned:
            conditions.append("(c.assigned_to = ? OR c.assigned_to IS NULL)")
            params.append(agent_id)
        else:
            conditions.append("c.assigned_to = ?")
            params.append(agent_id)
            
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY c.last_message_time DESC"
    
    cursor.execute(query, tuple(params))
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
    SELECT * FROM messages WHERE jid = ? ORDER BY timestamp DESC LIMIT ?
    ''', (jid, limit))
    rows = cursor.fetchall()
    conn.close()
    result = [_coerce_message_row(row) for row in rows]
    result.reverse() # Reorder to chronological (oldest to newest)
    return result

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

# --- AGENT AND INSTANCE MANAGEMENT FOR MULTI-ATENDIMENTO ---

def create_agent(name, email, password_hash, role='agent'):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO agents (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, 'offline')
        ''', (name, email, password_hash, role))
        conn.commit()
        agent_id = cursor.lastrowid
        return agent_id
    except Exception as e:
        print(f"Error creating agent: {e}")
        return None
    finally:
        conn.close()

def get_agent_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_agent_by_id(agent_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_agents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, status FROM agents ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_agent(agent_id, name=None, email=None, password_hash=None, role=None, status=None):
    conn = get_db()
    cursor = conn.cursor()
    if name is not None:
        cursor.execute("UPDATE agents SET name = ? WHERE id = ?", (name, agent_id))
    if email is not None:
        cursor.execute("UPDATE agents SET email = ? WHERE id = ?", (email, agent_id))
    if password_hash is not None:
        cursor.execute("UPDATE agents SET password_hash = ? WHERE id = ?", (password_hash, agent_id))
    if role is not None:
        cursor.execute("UPDATE agents SET role = ? WHERE id = ?", (role, agent_id))
    if status is not None:
        cursor.execute("UPDATE agents SET status = ? WHERE id = ?", (status, agent_id))
    conn.commit()
    conn.close()

def delete_agent(agent_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
    conn.commit()
    conn.close()

def create_instance(name, token=None, status='close'):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO instances (name, token, status)
        VALUES (?, ?, ?)
        ''', (name, token, status))
        conn.commit()
        inst_id = cursor.lastrowid
        return inst_id
    except Exception as e:
        print(f"Error creating instance: {e}")
        return None
    finally:
        conn.close()

def get_instance_by_name(name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instances WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_instance_by_id(instance_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instances WHERE id = ?", (instance_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_instances():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instances ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_instance_status(name, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE instances SET status = ? WHERE name = ?", (status, name))
    conn.commit()
    conn.close()

def update_instance_token(name, token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE instances SET token = ? WHERE name = ?", (token, name))
    conn.commit()
    conn.close()

def delete_instance(instance_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
    conn.commit()
    conn.close()

def link_agent_instance(agent_id, instance_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO agent_instances (agent_id, instance_id)
        VALUES (?, ?)
        ''', (agent_id, instance_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error linking agent/instance: {e}")
        return False
    finally:
        conn.close()

def unlink_agent_instance(agent_id, instance_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agent_instances WHERE agent_id = ? AND instance_id = ?", (agent_id, instance_id))
    conn.commit()
    conn.close()

def get_agent_instances(agent_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT i.* FROM instances i
    JOIN agent_instances ai ON ai.instance_id = i.id
    WHERE ai.agent_id = ?
    ''', (agent_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_instance_agents(instance_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT a.id, a.name, a.email, a.role, a.status FROM agents a
    JOIN agent_instances ai ON ai.agent_id = a.id
    WHERE ai.instance_id = ?
    ''', (instance_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def assign_contact_to_agent(jid, agent_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET assigned_to = ? WHERE jid = ?", (agent_id, jid))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
