from flask import Flask, request, jsonify, send_from_directory, Response, redirect
from werkzeug.utils import secure_filename
from evolution_api import EvolutionClient
from utils import get_offer_files
import os
import json
import base64
import datetime
import threading
import csv
import io
from dotenv import load_dotenv

load_dotenv()

# Configuração de Backend (SQLite vs Postgres)
USE_POSTGRES = os.getenv("USE_POSTGRES", "0") == "1"
if USE_POSTGRES:
    from database_pg import init_db, save_message, update_contact, get_all_chats, get_chat_history, get_message_by_id, mark_as_read, get_metrics, get_all_contacts_from_db, is_message_processed, list_contact_groups, create_contact_group, rename_contact_group, delete_contact_group, add_group_members, get_group_members, remove_group_members, list_flows, get_active_flow, create_flow, rename_flow, set_active_flow, delete_flow, list_flow_rules, create_flow_rule, update_flow_rule, delete_flow_rule
else:
    from database import init_db, save_message, update_contact, get_all_chats, get_chat_history, get_message_by_id, mark_as_read, get_metrics, get_all_contacts_from_db, is_message_processed, list_contact_groups, create_contact_group, rename_contact_group, delete_contact_group, add_group_members, get_group_members, remove_group_members, list_flows, get_active_flow, create_flow, rename_flow, set_active_flow, delete_flow, list_flow_rules, create_flow_rule, update_flow_rule, delete_flow_rule

# Configuração de Fila (Redis vs Threads)
USE_REDIS_QUEUE = os.getenv("USE_REDIS_QUEUE", "0") == "1"
redis_queue = None
if USE_REDIS_QUEUE:
    try:
        from redis import Redis
        from rq import Queue
        REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        REDIS_PORT = os.getenv("REDIS_PORT", "6379")
        r_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)
        redis_queue = Queue('default', connection=r_conn)
        print(f"Redis Queue ativada em {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"Erro ao conectar Redis: {e}. Voltando para Threads.")
        USE_REDIS_QUEUE = False

from constants import *
from logger import log_message

app = Flask(__name__)
client = EvolutionClient()
try:
    init_db()
except Exception as e:
    print(f"DB init failed: {e}")

contact_sync_state = {
    "running": False,
    "last": None,
    "last_error": None,
    "last_at": None
}
contact_sync_lock = threading.Lock()

def _run_contact_sync():
    with contact_sync_lock:
        contact_sync_state["running"] = True
        contact_sync_state["last_error"] = None
        contact_sync_state["last"] = None

    imported = 0
    skipped = 0
    try:
        local_client = EvolutionClient()
        resp = local_client.fetch_contacts()
        if not isinstance(resp, list):
            raise ValueError("fetch_contacts did not return a list")

        for c in resp:
            if not isinstance(c, dict):
                skipped += 1
                continue

            raw_jid = c.get("remoteJid") or c.get("jid") or c.get("id") or c.get("number")
            if not raw_jid:
                skipped += 1
                continue

            jid = _normalize_jid(raw_jid)
            if not _is_valid_jid(jid) or jid.endswith("@g.us"):
                skipped += 1
                continue

            push_name = c.get("pushName") or c.get("push_name") or c.get("name") or c.get("notify") or None
            update_contact(jid, push_name=push_name)
            imported += 1

        with contact_sync_lock:
            contact_sync_state["last"] = {"imported": imported, "skipped": skipped}
            contact_sync_state["last_at"] = datetime.datetime.now().isoformat()
    except Exception as e:
        with contact_sync_lock:
            contact_sync_state["last_error"] = str(e)
            contact_sync_state["last_at"] = datetime.datetime.now().isoformat()
    finally:
        with contact_sync_lock:
            contact_sync_state["running"] = False

def _redact_webhook_payload(payload):
    if not isinstance(payload, dict):
        return payload
    redacted = dict(payload)
    if "apikey" in redacted:
        redacted["apikey"] = "REDACTED"
    return redacted

def _send_text_and_persist(client_obj, target_number, text):
    resp = client_obj.send_text(target_number, text)
    msg_id = None
    if isinstance(resp, dict):
        msg_id = (resp.get("key") or {}).get("id")
    if not msg_id:
        msg_id = "out_" + str(datetime.datetime.now().timestamp())
    save_message(
        msg_id=msg_id,
        jid=target_number,
        sender="bot",
        content=text,
        from_me=1
    )

def _process_message_async(target_number, message_content):
    try:
        local_client = EvolutionClient()
        if message_content == "1":
            files = get_offer_files()
            if files:
                _send_text_and_persist(
                    local_client,
                    target_number,
                    "Aguarde enquanto preparamos as ofertas para você economizar muito, e jajá enviamos!\n\nCaso não receba, pedimos que faça a solicitação novamente! :)\n\n\nAtenciosamente,\n\nSupermercados Caíque"
                )
                for f in files:
                    m_type = "document" if f.endswith(".pdf") else "image"
                    resp_media = local_client.send_media_base64(target_number, f, media_type=m_type)
                    log_message(f"Media Response ({f}): {resp_media}")
            else:
                _send_text_and_persist(local_client, target_number, "No momento não temos arquivos de ofertas cadastrados.")
        elif message_content == "2":
            _send_text_and_persist(local_client, target_number, TEXT_2_PAGAMENTO)
        elif message_content == "3":
            _send_text_and_persist(local_client, target_number, TEXT_3_ENTREGAS)
        elif message_content == "4":
            _send_text_and_persist(local_client, target_number, TEXT_4_VENDA)
        elif message_content == "5":
            _send_text_and_persist(local_client, target_number, TEXT_5_PARCELAMENTO)
        elif message_content == "6":
            _send_text_and_persist(local_client, target_number, TEXT_6_PRECOS)
        elif message_content == "7":
            _send_text_and_persist(local_client, target_number, TEXT_7_ATENDENTE)
        elif message_content == "8":
            _send_text_and_persist(local_client, target_number, TEXT_8_TRABALHO)
        elif message_content == "9":
            _send_text_and_persist(local_client, target_number, TEXT_9_ENCERRAR)
        elif "eu quero" in message_content:
            _send_text_and_persist(local_client, target_number, TEXT_EU_QUERO)
        elif "obrigado" in message_content:
            _send_text_and_persist(local_client, target_number, TEXT_OBRIGADO)
        elif "atendente" in message_content:
            _send_text_and_persist(local_client, target_number, TEXT_7_ATENDENTE)
        else:
            log_message("Sending Menu")
            _send_text_and_persist(local_client, target_number, MENU_TEXT)
    except Exception as e:
        log_message(f"Error processing message async: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    if os.getenv("WEBHOOK_DUMP") == "1":
        with open("last_webhook.json", "w", encoding="utf-8") as f:
            json.dump(_redact_webhook_payload(data), f, indent=2, ensure_ascii=False)

    # Evolution API structure often resembles:
    # { "event": "messages.upsert", "data": { "key": {"remoteJid": "..."}, "message": {...} } }
    # OR sometimes simplified depending on version.
    
    # We look for 'data' key usually
    event_data = data.get('data')
    if not event_data:
        # Sometimes it's directly in the root or 'message'
        event_data = data
        
    print(f"Processing event_data keys: {list(event_data.keys())}")

    # SAFEGUARD: Only process 'messages.upsert' events for AutoResponder
    event_type = data.get('event')
    if event_type != "messages.upsert":
        log_message(f"Ignored event type: {event_type}")
        return jsonify({"status": "ignored", "reason": "not_upsert"}), 200

    # Check if message
    if 'key' not in event_data:
        print("Ignored: No 'key' found in data.")
        return jsonify({"status": "ignored", "reason": "no key"}), 200

    msg_id = event_data['key'].get('id')
    if not msg_id:
        return jsonify({"status": "ignored", "reason": "no_msg_id"}), 200

    # IDEMPOTENCY CHECK
    if is_message_processed(msg_id):
        log_message(f"Ignored: Already processed message {msg_id}")
        return jsonify({"status": "ignored", "reason": "already_processed"}), 200

    # Priority: key.remoteJid (LID or Phone)
    remote_jid = event_data['key'].get('remoteJid')
    from_me = event_data['key'].get('fromMe', False)
    sender_num = data.get('sender')
    
    log_message(f"Incoming: JID={remote_jid}, Sender={sender_num}, FromMe={from_me}")

    if from_me:
         log_message("Ignored: fromMe=True")
         return jsonify({"status": "ignored", "reason": "fromMe"}), 200

    if sender_num is None:
        log_message("Ignored: sender=None (likely bot's own message)")
        return jsonify({"status": "ignored", "reason": "no_sender"}), 200
    
    if remote_jid and remote_jid.endswith("@lid"):
        LID_TO_PHONE_MAP = {
            "135768261533797@lid": "556195338876@s.whatsapp.net",
            "96739944046708@lid": "556181056733@s.whatsapp.net",
            "229295486152753@lid": "556181322289@s.whatsapp.net",
        }

        if remote_jid in LID_TO_PHONE_MAP:
            target_number = LID_TO_PHONE_MAP[remote_jid]
            log_message(f"Using manual LID mapping: {remote_jid} -> {target_number}")
        else:
            target_number = remote_jid
            log_message(f"LID received (no mapping). Replying using LID: {target_number}")
    else:
        target_number = remote_jid
    
    log_message(f"Final target for reply: {target_number}")
    
    # BLOCKED NUMBERS: Do not send messages to these numbers
    BLOCKED_NUMBERS = [
        "556181322889@s.whatsapp.net",
        "5561813228890@s.whatsapp.net",  # Alternative format
    ]
    
    if target_number in BLOCKED_NUMBERS:
        log_message(f"BLOCKED: Not sending to blocked number {target_number}")
        return jsonify({"status": "ignored", "reason": "blocked_number"}), 200

    # SAFEGUARD: Ignore Group Messages
    if target_number.endswith("@g.us"):
        log_message(f"Ignored: Group message from {target_number}")
        return jsonify({"status": "ignored", "reason": "group_message"}), 200

    # SAFEGUARD: Ignore Old Messages (Backlog protection)
    msg_timestamp = event_data.get('messageTimestamp')
    if msg_timestamp:
        now = datetime.datetime.now().timestamp()
        age = now - msg_timestamp
        if age > 300: # 5 minutes
            log_message(f"Ignored: Old message (age={int(age)}s)")
            return jsonify({"status": "ignored", "reason": "old_message"}), 200
         
    # Extract Message Content
    msg_obj = event_data.get('message', {})
    raw_message_content = ""
    
    if 'conversation' in msg_obj:
        raw_message_content = msg_obj['conversation']
    elif 'extendedTextMessage' in msg_obj:
        raw_message_content = msg_obj['extendedTextMessage'].get('text', "")
    elif 'imageMessage' in msg_obj:
        raw_message_content = msg_obj['imageMessage'].get('caption', "")
    elif 'videoMessage' in msg_obj:
        raw_message_content = msg_obj['videoMessage'].get('caption', "")

    # For routing/processing, we use stripped and lowered version
    message_content = raw_message_content.strip().lower()
    log_message(f"Extracted Content: '{raw_message_content}' -> Processed: '{message_content}'")
    log_message(f"Processing command: {message_content}")
    
    # -- PERSIST TO DATABASE --
    msg_id = event_data['key'].get('id', 'temp_' + str(datetime.datetime.now().timestamp()))
    push_name = event_data.get('pushName', 'Unknown')
    
    # Extract type and metadata for DB
    msg_type = 'text'
    metadata = {}
    
    if 'imageMessage' in msg_obj:
        msg_type = 'image'
        im = msg_obj.get('imageMessage') or {}
        metadata['mimetype'] = im.get('mimetype')
        if im.get('jpegThumbnail') is not None:
            metadata['jpegThumbnail'] = im.get('jpegThumbnail')
    elif 'audioMessage' in msg_obj:
        msg_type = 'audio'
    elif 'videoMessage' in msg_obj:
        msg_type = 'video'
        vm = msg_obj.get('videoMessage') or {}
        metadata['mimetype'] = vm.get('mimetype')
        if vm.get('jpegThumbnail') is not None:
            metadata['jpegThumbnail'] = vm.get('jpegThumbnail')
    
    # Save/Update Contact
    update_contact(target_number, push_name=push_name)
    
    # Save Message
    db_content = raw_message_content if raw_message_content else (f"[{msg_type}]" if msg_type != 'text' else "")
    save_message(
        msg_id=msg_id,
        jid=target_number,
        sender=target_number,
        content=db_content,
        msg_type=msg_type,
        metadata=metadata,
        from_me=0
    )

    if not message_content and msg_type == 'text':
        log_message("Ignored: No text content for routing")
        return jsonify({"status": "ignored", "reason": "no text"}), 200
    
    if USE_REDIS_QUEUE and redis_queue:
        try:
            from tasks import process_message_task
            redis_queue.enqueue(process_message_task, target_number, message_content)
            log_message(f"Enqueued message for {target_number} to Redis")
        except Exception as e:
            log_message(f"Redis enqueue failed: {e}. Falling back to Thread.")
            from tasks import process_message_task
            threading.Thread(target=process_message_task, args=(target_number, message_content), daemon=True).start()
    else:
        from tasks import process_message_task
        threading.Thread(target=process_message_task, args=(target_number, message_content), daemon=True).start()

    return jsonify({"status": "accepted"}), 200

# -- DASHBOARD API ENDPOINTS --

@app.route('/api/chats', methods=['GET'])
def api_get_chats():
    chats = get_all_chats()
    return jsonify(chats), 200

@app.route('/api/contacts', methods=['GET'])
def api_get_contacts():
    contacts = get_all_contacts_from_db()
    return jsonify(contacts), 200

@app.route('/api/contacts/sync', methods=['GET'])
def api_get_contacts_sync_status():
    with contact_sync_lock:
        return jsonify(dict(contact_sync_state)), 200

@app.route('/api/contacts/sync', methods=['POST'])
def api_sync_contacts():
    with contact_sync_lock:
        if contact_sync_state.get("running"):
            return jsonify({"status": "running"}), 200
        contact_sync_state["running"] = True
        contact_sync_state["last_error"] = None

    threading.Thread(target=_run_contact_sync, daemon=True).start()
    return jsonify({"status": "accepted"}), 200

@app.route('/api/contact-groups', methods=['GET', 'POST'])
def api_contact_groups():
    if request.method == 'GET':
        return jsonify(list_contact_groups()), 200

    data = request.json or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Missing name"}), 400

    try:
        group_id = create_contact_group(name)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if not group_id:
        return jsonify({"error": "Failed to create group"}), 400
    return jsonify({"status": "success", "id": group_id, "name": name}), 200

@app.route('/api/contact-groups/<int:group_id>', methods=['DELETE', 'PUT'])
def api_contact_group(group_id):
    if request.method == 'PUT':
        data = request.json or {}
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "Missing name"}), 400
        try:
            ok = rename_contact_group(group_id, name)
            if not ok:
                return jsonify({"error": "Failed to rename group"}), 400
            return jsonify({"status": "success", "id": group_id, "name": name}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    try:
        delete_contact_group(group_id)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/contact-groups/<int:group_id>/members', methods=['GET', 'POST', 'DELETE'])
def api_contact_group_members(group_id):
    if request.method == 'GET':
        try:
            return jsonify(get_group_members(group_id)), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    if request.method == 'DELETE':
        data = request.json or {}
        jids = data.get("jids") or []
        jid = data.get("jid")
        if jid:
            jids = [jid]
        if not isinstance(jids, list) or len(jids) == 0:
            return jsonify({"error": "Missing jid(s)"}), 400

        normalized = []
        for j in jids:
            nj = _normalize_jid(j)
            if _is_valid_jid(nj) and not nj.endswith("@g.us"):
                normalized.append(nj)

        removed = remove_group_members(group_id, normalized)
        return jsonify({"status": "success", "removed": removed}), 200

    data = request.json or {}
    jids = data.get("jids") or []
    contacts = data.get("contacts") or []

    normalized = []
    for j in jids:
        jid = _normalize_jid(j)
        if _is_valid_jid(jid) and not jid.endswith("@g.us"):
            update_contact(jid)
            normalized.append(jid)

    for c in contacts:
        if not isinstance(c, dict):
            continue
        jid = _normalize_jid(c.get("jid") or c.get("number") or c.get("phone"))
        if not _is_valid_jid(jid) or jid.endswith("@g.us"):
            continue
        update_contact(jid, push_name=c.get("push_name") or c.get("pushName") or c.get("name"))
        normalized.append(jid)

    added = add_group_members(group_id, normalized)
    return jsonify({"status": "success", "added": added}), 200

@app.route('/api/contact-groups/import-csv', methods=['POST'])
def api_import_group_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    f = request.files['file']
    if not f or not getattr(f, "filename", ""):
        return jsonify({"error": "No selected file"}), 400

    group_id = request.form.get('group_id')
    group_name = (request.form.get('group_name') or '').strip()

    if not group_id:
        if not group_name:
            group_name = os.path.splitext(secure_filename(f.filename))[0] or "Importado"
        try:
            group_id = create_contact_group(group_name)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    try:
        group_id = int(group_id)
    except Exception:
        return jsonify({"error": "Invalid group_id"}), 400

    raw = f.read()
    text = None
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            text = raw.decode(enc)
            break
        except Exception:
            continue
    if text is None:
        return jsonify({"error": "Unable to decode file"}), 400

    sample = text[:2048]
    delimiter = ","
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ";" if sample.count(";") > sample.count(",") else ","

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    def pick(row, keys):
        for k in keys:
            if k in row and row[k]:
                return row[k]
        return None

    imported = 0
    skipped = 0
    members = []

    for row in reader:
        if not isinstance(row, dict):
            skipped += 1
            continue
        lower_row = {str(k).strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k is not None}

        raw_jid = pick(lower_row, ["jid", "remotejid", "id", "numero", "número", "number", "phone", "telefone", "celular", "whatsapp"])
        if not raw_jid:
            skipped += 1
            continue

        jid = _normalize_jid(raw_jid)
        if not _is_valid_jid(jid) or jid.endswith("@g.us"):
            skipped += 1
            continue

        name = pick(lower_row, ["push_name", "pushname", "nome", "name", "contato"])
        update_contact(jid, push_name=name)
        imported += 1
        members.append(jid)

    added = add_group_members(group_id, members)
    return jsonify({"status": "success", "group_id": group_id, "imported": imported, "added_to_group": added, "skipped": skipped}), 200

@app.route('/api/flows', methods=['GET', 'POST'])
def api_flows():
    if request.method == 'GET':
        return jsonify(list_flows()), 200

    data = request.json or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Missing name"}), 400
    try:
        flow_id = create_flow(name, is_active=bool(data.get("is_active")))
        if not flow_id:
            return jsonify({"error": "Failed to create flow"}), 400
        if data.get("is_active"):
            set_active_flow(flow_id)
        return jsonify({"status": "success", "id": flow_id, "name": name}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/flows/<int:flow_id>', methods=['PUT', 'DELETE'])
def api_flow(flow_id):
    if request.method == 'PUT':
        data = request.json or {}
        name = data.get("name")
        is_active = data.get("is_active")
        try:
            if name is not None:
                new_name = (name or "").strip()
                if not new_name:
                    return jsonify({"error": "Missing name"}), 400
                ok = rename_flow(flow_id, new_name)
                if not ok:
                    return jsonify({"error": "Failed to rename flow"}), 400
            if is_active is True:
                ok = set_active_flow(flow_id)
                if not ok:
                    return jsonify({"error": "Failed to activate flow"}), 400
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    try:
        delete_flow(flow_id)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/flows/<int:flow_id>/rules', methods=['GET', 'POST'])
def api_flow_rules(flow_id):
    if request.method == 'GET':
        try:
            return jsonify(list_flow_rules(flow_id)), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    data = request.json or {}
    match_type = (data.get("match_type") or "").strip()
    action_type = (data.get("action_type") or "").strip()
    priority = data.get("priority", 100)
    match_value = data.get("match_value")
    action_value = data.get("action_value")
    enabled = data.get("enabled", True)

    if match_type not in ["exact", "contains", "default"]:
        return jsonify({"error": "Invalid match_type"}), 400
    if action_type not in ["text", "offers"]:
        return jsonify({"error": "Invalid action_type"}), 400
    if match_type != "default" and not (match_value or "").strip():
        return jsonify({"error": "Missing match_value"}), 400
    if action_type == "text" and not (action_value or "").strip():
        return jsonify({"error": "Missing action_value"}), 400

    try:
        rule_id = create_flow_rule(
            flow_id=flow_id,
            priority=priority,
            match_type=match_type,
            match_value=(match_value or None),
            action_type=action_type,
            action_value=(action_value or None),
            enabled=bool(enabled)
        )
        if not rule_id:
            return jsonify({"error": "Failed to create rule"}), 400
        return jsonify({"status": "success", "id": rule_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/flow-rules/<int:rule_id>', methods=['PUT', 'DELETE'])
def api_flow_rule(rule_id):
    if request.method == 'DELETE':
        try:
            delete_flow_rule(rule_id)
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    data = request.json or {}
    payload = {}
    if "priority" in data:
        payload["priority"] = data.get("priority")
    if "match_type" in data:
        payload["match_type"] = data.get("match_type")
    if "match_value" in data:
        payload["match_value"] = data.get("match_value")
    if "action_type" in data:
        payload["action_type"] = data.get("action_type")
    if "action_value" in data:
        payload["action_value"] = data.get("action_value")
    if "enabled" in data:
        payload["enabled"] = data.get("enabled")

    if "match_type" in payload and payload["match_type"] not in ["exact", "contains", "default"]:
        return jsonify({"error": "Invalid match_type"}), 400
    if "action_type" in payload and payload["action_type"] not in ["text", "offers"]:
        return jsonify({"error": "Invalid action_type"}), 400

    try:
        ok = update_flow_rule(rule_id, **payload)
        if not ok:
            return jsonify({"error": "Failed to update rule"}), 400
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/flows/bootstrap-default', methods=['POST'])
def api_bootstrap_default_flow():
    try:
        flows = list_flows()
        default_flow = None
        for f in flows:
            if (f.get("name") or "").strip().lower() == "fluxo padrão":
                default_flow = f
                break

        if not default_flow:
            flow_id = create_flow("Fluxo Padrão", is_active=True)
            if not flow_id:
                return jsonify({"error": "Failed to create default flow"}), 400
            set_active_flow(flow_id)
        else:
            flow_id = int(default_flow["id"])

        existing = list_flow_rules(flow_id)
        if not existing:
            create_flow_rule(flow_id, 10, "exact", "1", "offers", "Aguarde enquanto preparamos as ofertas para você economizar muito, e jajá enviamos!\n\nCaso não receba, pedimos que faça a solicitação novamente! :)\n\n\nAtenciosamente,\n\nSupermercados Caíque", True)
            create_flow_rule(flow_id, 15, "contains", "eu quero", "text", TEXT_EU_QUERO, True)
            create_flow_rule(flow_id, 16, "contains", "obrigado", "text", TEXT_OBRIGADO, True)
            create_flow_rule(flow_id, 17, "contains", "atendente", "text", TEXT_7_ATENDENTE, True)
            create_flow_rule(flow_id, 20, "exact", "2", "text", TEXT_2_PAGAMENTO, True)
            create_flow_rule(flow_id, 21, "exact", "3", "text", TEXT_3_ENTREGAS, True)
            create_flow_rule(flow_id, 22, "exact", "4", "text", TEXT_4_VENDA, True)
            create_flow_rule(flow_id, 23, "exact", "5", "text", TEXT_5_PARCELAMENTO, True)
            create_flow_rule(flow_id, 24, "exact", "6", "text", TEXT_6_PRECOS, True)
            create_flow_rule(flow_id, 25, "exact", "7", "text", TEXT_7_ATENDENTE, True)
            create_flow_rule(flow_id, 26, "exact", "8", "text", TEXT_8_TRABALHO, True)
            create_flow_rule(flow_id, 27, "exact", "9", "text", TEXT_9_ENCERRAR, True)
            create_flow_rule(flow_id, 999, "default", None, "text", MENU_TEXT, True)

        return jsonify({"status": "success", "flow_id": flow_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/messages/<jid>', methods=['GET'])
def api_get_messages(jid):
    history = get_chat_history(jid)
    # Automatically mark as read when fetching history
    mark_as_read(jid)
    return jsonify(history), 200

@app.route('/api/read/<jid>', methods=['POST'])
def api_mark_read(jid):
    mark_as_read(jid)
    return jsonify({"status": "success"}), 200

@app.route('/api/media/<msg_id>', methods=['GET'])
def api_get_media(msg_id):
    msg = get_message_by_id(msg_id)
    if not msg:
        return jsonify({"error": "Message not found"}), 404

    raw = bool(request.args.get("raw") == "1")

    md = msg.get("metadata") or {}
    local_url = md.get("local_url")
    if local_url and str(local_url).startswith("/api/files/"):
        if raw:
            return redirect(local_url)
        return jsonify({"url": local_url, "source": "local"}), 200

    convert_to_mp4 = bool(request.args.get("mp4") == "1")
    resp = client.get_base64_from_media_message(msg_id, convert_to_mp4=convert_to_mp4)
    if not resp or not isinstance(resp, dict):
        return jsonify({"error": "Failed to fetch media"}), 502

    candidate = None
    if isinstance(resp.get("base64"), str):
        candidate = resp.get("base64")
    elif isinstance(resp.get("media"), str):
        candidate = resp.get("media")
    elif isinstance(resp.get("data"), str):
        candidate = resp.get("data")
    elif isinstance(resp.get("response"), dict):
        for k in ["base64", "media", "data"]:
            v = resp["response"].get(k)
            if isinstance(v, str):
                candidate = v
                break

    if not candidate:
        return jsonify({"error": "Media not available"}), 404

    if candidate.startswith("data:"):
        if raw:
            try:
                header, b64 = candidate.split(",", 1)
                mimetype = header.split(":", 1)[1].split(";", 1)[0] if ":" in header else "application/octet-stream"
                return Response(base64.b64decode(b64), mimetype=mimetype)
            except Exception:
                return jsonify({"error": "Invalid data uri"}), 502
        return jsonify({"url": candidate, "source": "evolution"}), 200

    mimetype = md.get("mimetype") or resp.get("mimetype") or "application/octet-stream"
    if raw:
        try:
            return Response(base64.b64decode(candidate), mimetype=mimetype)
        except Exception:
            return jsonify({"error": "Invalid base64"}), 502
    return jsonify({"url": f"data:{mimetype};base64,{candidate}", "source": "evolution"}), 200

@app.route('/api/send', methods=['POST'])
def api_send_message():
    data = request.json
    jid = data.get('jid')
    text = data.get('text')
    
    if not jid or not text:
        return jsonify({"error": "Missing jid or text"}), 400
    
    jid = _normalize_jid(jid)
    if not _is_valid_jid(jid):
        return jsonify({"error": "Invalid jid", "jid": jid}), 400
    
    local_client = EvolutionClient()
    resp = local_client.send_text(jid, text)
    if not resp or not isinstance(resp, dict):
        return jsonify({"status": "error", "response": resp}), 502
    if isinstance(resp.get("status"), int) and resp["status"] >= 400:
        return jsonify({"status": "error", "response": resp}), 400
    if "key" not in resp:
        return jsonify({"status": "error", "response": resp}), 502
    
    # Save outgoing message to DB
    msg_id = resp.get('key', {}).get('id') if resp else 'out_' + str(datetime.datetime.now().timestamp())
    save_message(
        msg_id=msg_id,
        jid=jid,
        sender="bot",
        content=text,
        from_me=1
    )
    
    return jsonify({"status": "success", "response": resp}), 200

def _normalize_jid(value):
    if value is None:
        return None
    jid = str(value).strip()
    if "@lid" not in jid and "@g.us" not in jid:
        if "@" in jid:
            user, domain = jid.split("@", 1)
            user_digits = "".join([c for c in user if c.isdigit()])
            if user_digits:
                jid = f"{user_digits}@{domain}"
        else:
            user_digits = "".join([c for c in jid if c.isdigit()])
            if user_digits:
                jid = f"{user_digits}@s.whatsapp.net"
    return jid

def _is_valid_jid(jid):
    return bool(jid) and (jid.endswith("@s.whatsapp.net") or jid.endswith("@lid") or jid.endswith("@g.us"))

@app.route('/api/send/media', methods=['POST'])
def api_send_media():
    data = request.json or {}
    jid = data.get('jid')
    filename = data.get('filename')
    caption = data.get('caption', '') or ''

    if not jid or not filename:
        return jsonify({"error": "Missing jid or filename"}), 400

    jid = _normalize_jid(jid)
    if not _is_valid_jid(jid):
        return jsonify({"error": "Invalid jid", "jid": jid}), 400

    filename = secure_filename(str(filename))
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    path = os.path.join(OFFERS_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File not found", "filename": filename}), 404

    ext = os.path.splitext(filename)[1].lower()
    media_type = "document" if ext == ".pdf" else "image"

    local_client = EvolutionClient()
    resp = local_client.send_media_base64(jid, path, caption=caption, media_type=media_type)
    if not resp or not isinstance(resp, dict):
        return jsonify({"status": "error", "response": resp}), 502
    if isinstance(resp.get("status"), int) and resp["status"] >= 400:
        return jsonify({"status": "error", "response": resp}), 400
    if "key" not in resp:
        return jsonify({"status": "error", "response": resp}), 502

    msg_id = resp.get('key', {}).get('id') if resp else 'out_' + str(datetime.datetime.now().timestamp())
    local_url = f"/api/files/{filename}"
    save_message(
        msg_id=msg_id,
        jid=jid,
        sender="bot",
        content=local_url,
        msg_type=media_type,
        metadata={"filename": filename, "caption": caption, "local_url": local_url},
        from_me=1
    )

    return jsonify({"status": "success", "response": resp}), 200

@app.route('/api/instance/status', methods=['GET'])
def api_instance_status():
    # fetch_instance_details uses the 'fetchInstances' endpoint,
    # which is more reliable than 'connectionStatus' for overall state.
    details = client.fetch_instance_details()
    
    # Initialize basic status
    status = {
        "instance_name": client.instance_name,
        "instance": {
            "state": "disconnected",
            "ownerJid": "Não disponível"
        }
    }
    
    if details and isinstance(details, dict):
        # Extract state: 'open' is what the frontend expects for 'online'
        state = details.get('state') or details.get('connectionStatus')
        if not state and details.get('status') == 'connected':
            state = 'open'
        
        status['instance']['state'] = state or 'disconnected'
        status['instance']['ownerJid'] = details.get('ownerJid') or details.get('number') or "Não disponível"
        
        # Merge any other useful fields
        for key in ['name', 'status', 'token', 'connectionStatus']:
            if key in details:
                status['instance'][key] = details[key]
    elif details and isinstance(details, list):
        chosen = None
        for inst in details:
            if inst.get('name') == client.instance_name:
                chosen = inst
                break
        if chosen is None and len(details) > 0:
            chosen = details[0]
        if chosen:
            state = chosen.get('state') or chosen.get('connectionStatus')
            if not state and chosen.get('status') == 'connected':
                state = 'open'
            status['instance']['state'] = state or 'disconnected'
            status['instance']['ownerJid'] = chosen.get('ownerJid') or chosen.get('number') or "Não disponível"
            for key in ['name', 'status', 'token', 'connectionStatus']:
                if key in chosen:
                    status['instance'][key] = chosen[key]

    return jsonify(status), 200

@app.route('/api/config', methods=['GET'])
def api_get_config():
    """Expose the current server-side configuration to the frontend."""
    return jsonify({
        "url": client.base_url,
        "instance": client.instance_name
    }), 200

@app.route('/api/metrics', methods=['GET'])
def api_get_metrics():
    """Return database metrics for the dashboard."""
    metrics = get_metrics()
    return jsonify(metrics), 200

@app.route('/api/instance/logout', methods=['POST'])
def api_instance_logout():
    resp = client.logout_instance()
    return jsonify(resp), 200

@app.route('/api/instance/restart', methods=['POST'])
def api_instance_restart():
    resp = client.restart_instance()
    return jsonify(resp), 200

@app.route('/api/contacts/update', methods=['POST'])
def api_update_contact():
    data = request.json
    jid = data.get('jid')
    if not jid:
        return jsonify({"error": "Missing jid"}), 400
        
    update_contact(
        jid, 
        notes=data.get('notes'), 
        tags=data.get('tags'),
        is_favorite=data.get('is_favorite'),
        is_archived=data.get('is_archived')
    )
    return jsonify({"status": "success"}), 200

@app.route('/api/contacts/avatar', methods=['POST'])
def api_get_avatar():
    data = request.json
    jid = data.get('jid')
    if not jid:
        return jsonify({"error": "Missing jid"}), 400
    
    resp = client.fetch_profile_picture(jid)
    if resp and isinstance(resp, dict) and resp.get("profilePictureUrl"):
        update_contact(jid, profile_pic=resp.get("profilePictureUrl"))
    return jsonify(resp), 200

@app.route('/api/instance/presence', methods=['POST'])
def api_send_presence():
    data = request.json
    jid = data.get('jid')
    presence = data.get('presence', 'composing')
    if not jid:
        return jsonify({"error": "Missing jid"}), 400
    
    resp = client.send_presence(jid, presence)
    return jsonify(resp), 200

# -- FILE MANAGER API --

OFFERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ofertas"))

@app.route('/api/files', methods=['GET'])
def api_list_files():
    if not os.path.exists(OFFERS_DIR):
        os.makedirs(OFFERS_DIR)
    
    files = []
    for filename in os.listdir(OFFERS_DIR):
        path = os.path.join(OFFERS_DIR, filename)
        if os.path.isfile(path):
            stats = os.stat(path)
            files.append({
                "name": filename,
                "size": f"{stats.st_size / (1024*1024):.2f} MB" if stats.st_size > 1024*1024 else f"{stats.st_size / 1024:.2f} KB",
                "type": os.path.splitext(filename)[1].upper()[1:] + " Document"
            })
    return jsonify(files), 200

@app.route('/api/files/upload', methods=['POST'])
def api_upload_file():
    files = []
    if 'files' in request.files:
        files = request.files.getlist('files')
    elif 'file' in request.files:
        files = request.files.getlist('file')
    else:
        return jsonify({"error": "No file part"}), 400

    valid_files = [f for f in files if f and getattr(f, "filename", "")]
    if not valid_files:
        return jsonify({"error": "No selected file"}), 400

    if not os.path.exists(OFFERS_DIR):
        os.makedirs(OFFERS_DIR)

    saved = []
    for f in valid_files:
        filename = secure_filename(f.filename)
        if not filename:
            continue
        f.save(os.path.join(OFFERS_DIR, filename))
        saved.append(filename)

    if not saved:
        return jsonify({"error": "No selected file"}), 400

    if len(saved) == 1:
        return jsonify({"status": "success", "filename": saved[0]}), 200
    return jsonify({"status": "success", "filenames": saved}), 200

@app.route('/api/files/<filename>', methods=['GET', 'PUT', 'DELETE'])
def api_file_item(filename):
    filename = secure_filename(filename)
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    path = os.path.join(OFFERS_DIR, filename)

    if request.method == 'GET':
        if not os.path.exists(path):
            return jsonify({"error": "File not found"}), 404
        return send_from_directory(OFFERS_DIR, filename)

    if request.method == 'PUT':
        data = request.json or {}
        new_name = data.get('new_name')
        if not new_name:
            return jsonify({"error": "Missing new_name"}), 400

        new_name = str(new_name).strip()
        old_ext = os.path.splitext(filename)[1]
        if "." not in new_name:
            new_name = f"{new_name}{old_ext}"

        new_filename = secure_filename(new_name)
        if not new_filename:
            return jsonify({"error": "Invalid new_name"}), 400

        new_path = os.path.join(OFFERS_DIR, new_filename)
        if not os.path.exists(path):
            return jsonify({"error": "File not found"}), 404
        if os.path.exists(new_path):
            return jsonify({"error": "A file with this name already exists"}), 409

        os.rename(path, new_path)
        return jsonify({"status": "success", "filename": new_filename}), 200

    if os.path.exists(path):
        os.remove(path)
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "File not found"}), 404

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    print("Starting Webhook Server on port 3000 (0.0.0.0)...")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3000"))
    debug = os.getenv("FLASK_DEBUG") == "1"
    app.run(host=host, port=port, debug=debug)
