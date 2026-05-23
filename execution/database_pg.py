import os
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import json
from dotenv import load_dotenv

load_dotenv()

# Configuração via variáveis de ambiente
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "agente_whatsapp")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

def init_db():
    """Inicializa as tabelas no PostgreSQL."""
    conn = get_db_connection()
    if not conn:
        print("Falha ao conectar para inicializar banco.")
        return

    cursor = conn.cursor()
    
    # Tabela de Contatos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        jid TEXT PRIMARY KEY,
        push_name TEXT,
        profile_pic TEXT,
        notes TEXT,
        tags TEXT,
        is_favorite BOOLEAN DEFAULT FALSE,
        is_archived BOOLEAN DEFAULT FALSE,
        unread_count INTEGER DEFAULT 0,
        last_message_time TIMESTAMP
    );
    ''')
    
    # Tabela de Mensagens
    # No Postgres, BOOLEAN é o tipo nativo (0/1 funciona, mas True/False é melhor)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        jid TEXT REFERENCES contacts(jid),
        sender TEXT,
        content TEXT,
        type TEXT DEFAULT 'text',
        metadata TEXT,
        timestamp TIMESTAMP,
        from_me BOOLEAN DEFAULT FALSE,
        is_read BOOLEAN DEFAULT FALSE,
        status TEXT DEFAULT 'sent'
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_groups (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_group_members (
        group_id INTEGER NOT NULL REFERENCES contact_groups(id),
        jid TEXT NOT NULL REFERENCES contacts(jid),
        added_at TIMESTAMP,
        PRIMARY KEY (group_id, jid)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flows (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        is_active BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flow_rules (
        id SERIAL PRIMARY KEY,
        flow_id INTEGER NOT NULL REFERENCES flows(id) ON DELETE CASCADE,
        priority INTEGER DEFAULT 100,
        match_type TEXT NOT NULL,
        match_value TEXT,
        action_type TEXT NOT NULL,
        action_value TEXT,
        enabled BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Tabelas PostgreSQL verificadas/criadas.")

def save_message(msg_id, jid, sender, content, msg_type='text', metadata=None, from_me=0):
    conn = get_db_connection()
    if not conn: return

    cursor = conn.cursor()
    timestamp = datetime.datetime.now()
    metadata_json = json.dumps(metadata) if metadata else None
    
    # Converter 0/1 para Boolean se necessário, mas Postgres aceita ints em alguns contextos
    # Vamos garantir bool
    is_from_me = bool(from_me)
    is_read = bool(from_me) # Se for meu, já nasce lida
    
    try:
        # Upsert (Insert ou Update)
        cursor.execute('''
        INSERT INTO messages (id, jid, sender, content, type, metadata, timestamp, from_me, is_read)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET status = EXCLUDED.status;
        ''', (msg_id, jid, sender, content, msg_type, metadata_json, timestamp, is_from_me, is_read))
        
        # Atualizar contato
        if not is_from_me:
            cursor.execute('''
            UPDATE contacts SET last_message_time = %s, unread_count = unread_count + 1 WHERE jid = %s
            ''', (timestamp, jid))
        else:
            cursor.execute('''
            UPDATE contacts SET last_message_time = %s WHERE jid = %s
            ''', (timestamp, jid))
            
        conn.commit()
    except Exception as e:
        print(f"Erro ao salvar mensagem: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def mark_as_read(jid):
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE messages SET is_read = TRUE WHERE jid = %s", (jid,))
        cursor.execute("UPDATE contacts SET unread_count = 0 WHERE jid = %s", (jid,))
        conn.commit()
    except Exception as e:
        print(f"Erro mark_as_read: {e}")
    finally:
        cursor.close()
        conn.close()

def update_contact(jid, push_name=None, notes=None, tags=None, is_favorite=None, is_archived=None):
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        # Upsert do contato
        cursor.execute('''
        INSERT INTO contacts (jid, push_name) VALUES (%s, %s)
        ON CONFLICT (jid) DO NOTHING;
        ''', (jid, push_name))
        
        if push_name:
            cursor.execute("UPDATE contacts SET push_name = %s WHERE jid = %s", (push_name, jid))
        if notes is not None:
            cursor.execute("UPDATE contacts SET notes = %s WHERE jid = %s", (notes, jid))
        if tags is not None:
            cursor.execute("UPDATE contacts SET tags = %s WHERE jid = %s", (json.dumps(tags), jid))
        if is_favorite is not None:
            cursor.execute("UPDATE contacts SET is_favorite = %s WHERE jid = %s", (bool(is_favorite), jid))
        if is_archived is not None:
            cursor.execute("UPDATE contacts SET is_archived = %s WHERE jid = %s", (bool(is_archived), jid))
            
        conn.commit()
    except Exception as e:
        print(f"Erro update_contact: {e}")
    finally:
        cursor.close()
        conn.close()

def convert_dates(rows):
    """Converte objetos datetime em strings ISO 8601 para serialização JSON."""
    for row in rows:
        for key, value in row.items():
            if isinstance(value, datetime.datetime):
                row[key] = value.isoformat()
    return rows

def get_all_chats():
    conn = get_db_connection()
    if not conn: return []
    # Usar RealDictCursor para retornar dicionários como no sqlite3.Row
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute('''
        SELECT c.*, m.content as last_msg, m.timestamp as last_time
        FROM contacts c
        LEFT JOIN messages m ON m.id = (
            SELECT id FROM messages WHERE jid = c.jid ORDER BY timestamp DESC LIMIT 1
        )
        ORDER BY c.last_message_time DESC NULLS LAST
        ''')
        rows = cursor.fetchall()
        # RealDictCursor já retorna dicts, mas vamos garantir conversão se necessário
        result = [dict(row) for row in rows]
        return convert_dates(result)
    except Exception as e:
        print(f"Erro get_all_chats: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def _coerce_message_row(row):
    if not row:
        return row
    d = dict(row)
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
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute('''
        SELECT * FROM messages WHERE jid = %s ORDER BY timestamp ASC LIMIT %s
        ''', (jid, limit))
        rows = cursor.fetchall()
        result = [_coerce_message_row(row) for row in rows]
        return convert_dates(result)
    except Exception as e:
        print(f"Erro get_chat_history: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_message_by_id(msg_id):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM messages WHERE id = %s LIMIT 1", (msg_id,))
        row = cursor.fetchone()
        if not row:
            return None
        result = _coerce_message_row(row)
        result = convert_dates([result])
        return result[0] if result else None
    except Exception as e:
        print(f"Erro get_message_by_id: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_metrics():
    conn = get_db_connection()
    if not conn: return {"contacts": 0, "messages": 0, "chats": 0}
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM contacts")
        contacts_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        messages_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT jid) FROM messages")
        chats_count = cursor.fetchone()[0]
        
        return {
            "contacts": contacts_count,
            "messages": messages_count,
            "chats": chats_count
        }
    except Exception as e:
        print(f"Erro get_metrics: {e}")
        return {"contacts": 0, "messages": 0, "chats": 0}
    finally:
        cursor.close()
        conn.close()

def get_all_contacts_from_db():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM contacts ORDER BY push_name ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Erro get_all_contacts_from_db: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def list_contact_groups():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT id, name, created_at FROM contact_groups ORDER BY name ASC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Erro list_contact_groups: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def create_contact_group(name):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    now = datetime.datetime.now()
    try:
        cursor.execute("INSERT INTO contact_groups (name, created_at) VALUES (%s, %s) RETURNING id", (name, now))
        group_id = cursor.fetchone()[0]
        conn.commit()
        return group_id
    except Exception as e:
        print(f"Erro create_contact_group: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def rename_contact_group(group_id, new_name):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE contact_groups SET name = %s WHERE id = %s", (new_name, group_id))
        changed = cursor.rowcount and cursor.rowcount > 0
        conn.commit()
        return bool(changed)
    except Exception as e:
        print(f"Erro rename_contact_group: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def delete_contact_group(group_id):
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM contact_group_members WHERE group_id = %s", (group_id,))
        cursor.execute("DELETE FROM contact_groups WHERE id = %s", (group_id,))
        conn.commit()
    except Exception as e:
        print(f"Erro delete_contact_group: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_group_members(group_id, jids):
    conn = get_db_connection()
    if not conn: return 0
    cursor = conn.cursor()
    now = datetime.datetime.now()
    added = 0
    try:
        for jid in jids:
            if not jid:
                continue
            cursor.execute(
                "INSERT INTO contact_group_members (group_id, jid, added_at) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (group_id, jid, now)
            )
            if cursor.rowcount and cursor.rowcount > 0:
                added += 1
        conn.commit()
        return added
    except Exception as e:
        print(f"Erro add_group_members: {e}")
        conn.rollback()
        return added
    finally:
        cursor.close()
        conn.close()

def get_group_members(group_id):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute('''
        SELECT c.jid, c.push_name
        FROM contact_group_members gm
        JOIN contacts c ON c.jid = gm.jid
        WHERE gm.group_id = %s
        ORDER BY c.push_name ASC
        ''', (group_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Erro get_group_members: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def remove_group_members(group_id, jids):
    conn = get_db_connection()
    if not conn: return 0
    cursor = conn.cursor()
    removed = 0
    try:
        for jid in jids:
            if not jid:
                continue
            cursor.execute("DELETE FROM contact_group_members WHERE group_id = %s AND jid = %s", (group_id, jid))
            if cursor.rowcount and cursor.rowcount > 0:
                removed += 1
        conn.commit()
        return removed
    except Exception as e:
        print(f"Erro remove_group_members: {e}")
        conn.rollback()
        return removed
    finally:
        cursor.close()
        conn.close()

def list_flows():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT id, name, is_active, created_at, updated_at FROM flows ORDER BY is_active DESC, name ASC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Erro list_flows: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_active_flow():
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT id, name, is_active, created_at, updated_at FROM flows WHERE is_active = TRUE LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Erro get_active_flow: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_flow(name, is_active=False):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    now = datetime.datetime.now()
    try:
        cursor.execute(
            "INSERT INTO flows (name, is_active, created_at, updated_at) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, bool(is_active), now, now)
        )
        flow_id = cursor.fetchone()[0]
        conn.commit()
        return flow_id
    except Exception as e:
        print(f"Erro create_flow: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def rename_flow(flow_id, new_name):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    now = datetime.datetime.now()
    try:
        cursor.execute("UPDATE flows SET name = %s, updated_at = %s WHERE id = %s", (new_name, now, flow_id))
        changed = cursor.rowcount and cursor.rowcount > 0
        conn.commit()
        return bool(changed)
    except Exception as e:
        print(f"Erro rename_flow: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def set_active_flow(flow_id):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    now = datetime.datetime.now()
    try:
        cursor.execute("UPDATE flows SET is_active = FALSE, updated_at = %s WHERE is_active = TRUE", (now,))
        cursor.execute("UPDATE flows SET is_active = TRUE, updated_at = %s WHERE id = %s", (now, flow_id))
        changed = cursor.rowcount and cursor.rowcount > 0
        conn.commit()
        return bool(changed)
    except Exception as e:
        print(f"Erro set_active_flow: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def delete_flow(flow_id):
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM flow_rules WHERE flow_id = %s", (flow_id,))
        cursor.execute("DELETE FROM flows WHERE id = %s", (flow_id,))
        conn.commit()
    except Exception as e:
        print(f"Erro delete_flow: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def list_flow_rules(flow_id):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT id, flow_id, priority, match_type, match_value, action_type, action_value, enabled, created_at, updated_at
            FROM flow_rules
            WHERE flow_id = %s
            ORDER BY priority ASC, id ASC
        """, (flow_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Erro list_flow_rules: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def create_flow_rule(flow_id, priority, match_type, match_value, action_type, action_value, enabled=True):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    now = datetime.datetime.now()
    try:
        cursor.execute("""
            INSERT INTO flow_rules
                (flow_id, priority, match_type, match_value, action_type, action_value, enabled, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (flow_id, int(priority), match_type, match_value, action_type, action_value, bool(enabled), now, now))
        rule_id = cursor.fetchone()[0]
        conn.commit()
        return rule_id
    except Exception as e:
        print(f"Erro create_flow_rule: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def update_flow_rule(rule_id, priority=None, match_type=None, match_value=None, action_type=None, action_value=None, enabled=None):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    now = datetime.datetime.now()
    fields = []
    values = []
    if priority is not None:
        fields.append("priority = %s")
        values.append(int(priority))
    if match_type is not None:
        fields.append("match_type = %s")
        values.append(match_type)
    if match_value is not None:
        fields.append("match_value = %s")
        values.append(match_value)
    if action_type is not None:
        fields.append("action_type = %s")
        values.append(action_type)
    if action_value is not None:
        fields.append("action_value = %s")
        values.append(action_value)
    if enabled is not None:
        fields.append("enabled = %s")
        values.append(bool(enabled))
    if not fields:
        cursor.close()
        conn.close()
        return False
    fields.append("updated_at = %s")
    values.append(now)
    values.append(rule_id)
    try:
        cursor.execute(f"UPDATE flow_rules SET {', '.join(fields)} WHERE id = %s", values)
        changed = cursor.rowcount and cursor.rowcount > 0
        conn.commit()
        return bool(changed)
    except Exception as e:
        print(f"Erro update_flow_rule: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def delete_flow_rule(rule_id):
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM flow_rules WHERE id = %s", (rule_id,))
        conn.commit()
    except Exception as e:
        print(f"Erro delete_flow_rule: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def is_message_processed(msg_id):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM messages WHERE id = %s", (msg_id,))
        exists = cursor.fetchone() is not None
        return exists
    except Exception as e:
        print(f"Erro is_message_processed: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_db()
