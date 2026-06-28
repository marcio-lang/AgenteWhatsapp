import os
import datetime
from evolution_api import EvolutionClient
from utils import get_offer_files
from constants import *
from logger import log_message

USE_POSTGRES = os.getenv("USE_POSTGRES", "0") == "1"
if USE_POSTGRES:
    from database_pg import *
else:
    from database import *

def _send_text_and_persist(client_obj, target_number, text, instance_id=None):
    """Envia mensagem via API e persiste no banco configurado."""
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
        from_me=1,
        instance_id=instance_id
    )

def _ensure_default_flow():
    active = None
    try:
        active = get_active_flow()
    except Exception:
        active = None
    if active and active.get("id"):
        return int(active["id"])

    try:
        flows = list_flows()
        if isinstance(flows, list) and len(flows) > 0:
            first_id = flows[0].get("id")
            if first_id:
                set_active_flow(int(first_id))
                return int(first_id)
    except Exception:
        pass

    flow_id = create_flow("Fluxo Padrão", is_active=True)
    if not flow_id:
        return None
    try:
        set_active_flow(flow_id)
    except Exception:
        pass

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

    return flow_id

def _pick_rule(rules, message_content):
    default_rule = None
    msg = (message_content or "").strip().lower()
    for r in rules or []:
        if not r or not r.get("enabled"):
            continue
        mt = (r.get("match_type") or "").strip()
        mv = (r.get("match_value") or "")
        if mt == "default":
            if default_rule is None:
                default_rule = r
            continue
        mvn = str(mv).strip().lower()
        if mt == "exact" and msg == mvn:
            return r
        if mt == "contains" and mvn and (mvn in msg):
            return r
    return default_rule

def process_message_task(target_number, message_content, instance_id=None):
    try:
        log_message(f"[Worker] Processing message for {target_number} (Instance ID: {instance_id}): {message_content}")
        local_client = EvolutionClient()
        
        # Configure instance if provided
        if instance_id is not None:
            inst_details = get_instance_by_id(instance_id)
            if inst_details and inst_details.get("name"):
                local_client.instance_name = inst_details["name"]

        # Asynchronously fetch and update contact profile picture if not already present
        try:
            contacts = get_all_contacts_from_db()
            contact = next((c for c in contacts if c.get('jid') == target_number), None)
            if not contact or not contact.get("profile_pic"):
                log_message(f"[Worker] Profile picture missing for {target_number}, fetching from Evolution...")
                res_pic = local_client.fetch_profile_picture(target_number)
                if isinstance(res_pic, dict) and (res_pic.get("profilePictureUrl") or res_pic.get("url")):
                    pic_url = res_pic.get("profilePictureUrl") or res_pic.get("url")
                    log_message(f"[Worker] Found profile pic for {target_number}: {pic_url}")
                    update_contact(target_number, profile_pic=pic_url)
        except Exception as pic_err:
            log_message(f"[Worker] Error updating profile picture: {pic_err}")

        flow_id = _ensure_default_flow()
        rules = list_flow_rules(flow_id) if flow_id else []
        rule = _pick_rule(rules, message_content)

        if not rule:
            _send_text_and_persist(local_client, target_number, MENU_TEXT, instance_id)
            return

        action_type = (rule.get("action_type") or "").strip()
        action_value = rule.get("action_value") or ""

        if action_type == "text":
            _send_text_and_persist(local_client, target_number, str(action_value), instance_id)
            return

        if action_type == "offers":
            intro = str(action_value).strip()
            if intro:
                _send_text_and_persist(local_client, target_number, intro, instance_id)
            files = get_offer_files()
            if not files:
                _send_text_and_persist(local_client, target_number, "No momento não temos arquivos de ofertas cadastrados.", instance_id)
                return
            for f in files:
                m_type = "document" if str(f).lower().endswith(".pdf") else "image"
                resp_media = local_client.send_media_base64(target_number, f, media_type=m_type)
                log_message(f"[Worker] Media Response ({f}): {resp_media}")
                try:
                    msg_id = None
                    if isinstance(resp_media, dict):
                        msg_id = (resp_media.get("key") or {}).get("id")
                    if not msg_id:
                        msg_id = "out_" + str(datetime.datetime.now().timestamp())
                    filename = os.path.basename(str(f))
                    local_url = f"/api/files/{filename}"
                    save_message(
                        msg_id=msg_id,
                        jid=target_number,
                        sender="bot",
                        content=local_url,
                        msg_type=m_type,
                        metadata={"filename": filename, "local_url": local_url},
                        from_me=1,
                        instance_id=instance_id
                    )
                except Exception as e:
                    log_message(f"[Worker] Error persisting media message: {e}")
            return

        _send_text_and_persist(local_client, target_number, MENU_TEXT, instance_id)
            
    except Exception as e:
        log_message(f"[Worker] Error processing message: {e}")
