import os
import requests
import json
from dotenv import load_dotenv
import datetime

def log_message(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("server.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [API] {msg}\n")

load_dotenv()

class EvolutionClient:
    _cached_instance_name = None

    def __init__(self):
        full_url = os.getenv("EVOLUTION_API_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        env_instance_name = os.getenv("EVOLUTION_INSTANCE_NAME")
        
        if not full_url or not self.api_key:
            raise ValueError("Missing EVOLUTION_API_URL or EVOLUTION_API_KEY in .env")

        # Logic to separate Base URL and Instance Name
        if "/instance/" in full_url:
            parts = full_url.split("/instance/")
            self.base_url = parts[0]
            self.instance_name = parts[1].strip("/") or "chat"
        else:
            self.base_url = full_url
            self.instance_name = env_instance_name or "chat"

        if env_instance_name:
            self.instance_name = env_instance_name
            
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Create a session that ignores system proxies
        self.session = requests.Session()
        self.session.trust_env = False

        if EvolutionClient._cached_instance_name is None:
            EvolutionClient._cached_instance_name = self.instance_name
        else:
            self.instance_name = EvolutionClient._cached_instance_name

        if self.instance_name == "chat" and not env_instance_name:
            try:
                self._pick_active_instance_name()
            except Exception:
                pass

    def _pick_active_instance_name(self):
        instances = None
        for _ in range(3):
            instances = self.fetch_instance_details()
            if instances:
                break
        if isinstance(instances, list) and instances:
            for inst in instances:
                if inst.get("connectionStatus") == "open" and inst.get("name"):
                    EvolutionClient._cached_instance_name = inst["name"]
                    self.instance_name = inst["name"]
                    return self.instance_name
            if instances[0].get("name"):
                EvolutionClient._cached_instance_name = instances[0]["name"]
                self.instance_name = instances[0]["name"]
                return self.instance_name
        return self.instance_name

    def _maybe_fix_instance(self, resp_json):
        try:
            if isinstance(resp_json, dict):
                candidates = [
                    resp_json.get("message"),
                    (resp_json.get("response") or {}).get("message"),
                    resp_json.get("error"),
                ]
                for msg in candidates:
                    if msg and "instance does not exist" in str(msg).lower():
                        self._pick_active_instance_name()
                        return True
        except Exception:
            return False
        return False

    def send_text(self, number, text):
        """Sends a text message to a specific number."""
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        payload = {
            "number": number,
            "text": text,
            "delay": 1200,
            "linkPreview": True
        }
        log_message(f"Sending TEXT to {number} via {url}")
        try:
            # Use self.session instead of requests
            response = self.session.post(url, json=payload, headers=self.headers, timeout=10) 
            log_message(f"API Response: {response.status_code} - {response.text}")
            resp_json = response.json()
            if (response.status_code == 404 or (isinstance(resp_json, dict) and resp_json.get("status") == 404)) and self._maybe_fix_instance(resp_json):
                url = f"{self.base_url}/message/sendText/{self.instance_name}"
                log_message(f"Retrying TEXT to {number} via {url}")
                response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
                log_message(f"API Response (retry): {response.status_code} - {response.text}")
                return response.json()
            return resp_json
        except Exception as e:
            log_message(f"Error sending text: {e}")
            print(f"Error sending text: {e}")
            return None

    def find_contact(self, contact_id):
        """
        Finds contact information by ID (including LID resolution).
        Returns contact info from Evolution API.
        """
        url = f"{self.base_url}/chat/findContacts/{self.instance_name}"
        payloads = [
            {"where": {"id": contact_id}},
            {"where": {"remoteJid": contact_id}},
            {"where": {"jid": contact_id}},
        ]
        log_message(f"Finding contact: {contact_id} via {url}")
        try:
            last_json = None
            for payload in payloads:
                response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
                txt = response.text or ""
                log_message(f"Find Contact Response: {response.status_code} - {txt[:200]}")
                try:
                    last_json = response.json()
                except Exception:
                    last_json = None
                if (response.status_code == 404 or (isinstance(last_json, dict) and last_json.get("status") == 404)) and self._maybe_fix_instance(last_json):
                    url = f"{self.base_url}/chat/findContacts/{self.instance_name}"
                    continue
                if isinstance(last_json, list) and last_json:
                    return last_json
            return last_json
        except Exception as e:
            log_message(f"Error finding contact: {e}")
            print(f"Error finding contact: {e}")
            return None

    def fetch_contacts(self):
        candidates = [
            ("GET", f"{self.base_url}/chat/fetchContacts/{self.instance_name}", None),
            ("GET", f"{self.base_url}/chat/contacts/{self.instance_name}", None),
            ("POST", f"{self.base_url}/chat/findContacts/{self.instance_name}", {"where": {}}),
            ("POST", f"{self.base_url}/chat/findContacts/{self.instance_name}", {}),
            ("POST", f"{self.base_url}/chat/findContacts/{self.instance_name}", None),
        ]

        last_json = None
        for method, url, payload in candidates:
            try:
                if method == "GET":
                    response = self.session.get(url, headers=self.headers, timeout=15)
                else:
                    response = self.session.post(url, json=payload, headers=self.headers, timeout=15)
                txt = response.text or ""
                log_message(f"Fetch Contacts ({method}) {url}: {response.status_code} - {txt[:200]}")
                try:
                    last_json = response.json()
                except Exception:
                    last_json = None

                if (response.status_code == 404 or (isinstance(last_json, dict) and last_json.get("status") == 404)) and self._maybe_fix_instance(last_json):
                    candidates = [
                        ("GET", f"{self.base_url}/chat/fetchContacts/{self.instance_name}", None),
                        ("GET", f"{self.base_url}/chat/contacts/{self.instance_name}", None),
                        ("POST", f"{self.base_url}/chat/findContacts/{self.instance_name}", {"where": {}}),
                        ("POST", f"{self.base_url}/chat/findContacts/{self.instance_name}", {}),
                        ("POST", f"{self.base_url}/chat/findContacts/{self.instance_name}", None),
                    ]
                    continue

                if isinstance(last_json, list):
                    return last_json
                if isinstance(last_json, dict):
                    for key in ["contacts", "response", "data", "result"]:
                        val = last_json.get(key)
                        if isinstance(val, list):
                            return val
                        if isinstance(val, dict):
                            for nested_key in ["contacts", "data", "result"]:
                                nested_val = val.get(nested_key)
                                if isinstance(nested_val, list):
                                    return nested_val
            except Exception as e:
                log_message(f"Error fetching contacts via {url}: {e}")
                last_json = None

        return last_json

    def send_media_base64(self, number, file_path, caption="", media_type="image"):
        """
        Sends a local file as Base64.
        media_type: 'image' or 'document' (for PDF)
        """
        import base64
        import mimetypes

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        with open(file_path, "rb") as f:
            base64_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Evolution API can be picky about the base64 format. 
        # Usually it's "data:mime/type;base64,DATA"
        base64_full = f"data:{mime_type};base64,{base64_data}"

        url = f"{self.base_url}/message/sendMedia/{self.instance_name}"
        
        # Try sending with the data URI prefix first
        payload = {
            "number": number,
            "media": base64_full,
            "mediatype": media_type,
            "caption": caption
        }
        
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=30)
            resp_json = response.json()
            
            # If it failed with "Owned media must be a url or base64", 
            # it might expect just the raw base64 string.
            if response.status_code == 400 and "Owned media" in str(resp_json):
                print("Prefix failed, retrying with raw base64...")
                payload["media"] = base64_data
                response = self.session.post(url, json=payload, headers=self.headers, timeout=30)
                resp_json = response.json()

            print(f"Sent media response: {response.text}")
            return resp_json
        except Exception as e:
            print(f"Error sending media: {e}")
            return None

    def get_base64_from_media_message(self, message_id, convert_to_mp4=False):
        url = f"{self.base_url}/chat/getBase64FromMediaMessage/{self.instance_name}"
        payload = {
            "message": {
                "key": {
                    "id": str(message_id)
                }
            },
            "convertToMp4": bool(convert_to_mp4)
        }
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=30)
            try:
                return response.json()
            except Exception:
                return {"status": response.status_code, "raw": response.text}
        except Exception as e:
            log_message(f"Error get_base64_from_media_message for {message_id}: {e}")
            return None

    def get_instance_status(self):
        """Checks the connection status of the instance."""
        url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
        log_message(f"Checking status for instance: {self.instance_name} via {url}")
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            log_message(f"Error checking instance status: {e}")
            return {"instance": {"state": "error", "reason": str(e)}}

    def restart_instance(self):
        """Restarts the WhatsApp instance."""
        url = f"{self.base_url}/instance/restart/{self.instance_name}"
        log_message(f"Restarting instance: {self.instance_name} via {url}")
        try:
            response = self.session.post(url, headers=self.headers, timeout=15)
            return response.json()
        except Exception as e:
            log_message(f"Error restarting instance: {e}")
            return {"status": "error", "message": str(e)}

    def fetch_instance_details(self):
        """Fetches detailed information about the instance."""
        url = f"{self.base_url}/instance/fetchInstances"
        # Optional: query param or filter by name if API supports it, 
        # otherwise we filter manually.
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            instances = response.json()
            if isinstance(instances, list):
                for inst in instances:
                    if inst.get('name') == self.instance_name:
                        return inst
            return instances # Fallback
        except Exception as e:
            log_message(f"Error fetching instance details: {e}")
            return None

    def logout_instance(self):
        """Logs out/Disconnects the WhatsApp instance."""
        url = f"{self.base_url}/instance/logout/{self.instance_name}"
        log_message(f"Logging out instance: {self.instance_name} via {url}")
        try:
            response = self.session.delete(url, headers=self.headers, timeout=15)
            return response.json()
        except Exception as e:
            log_message(f"Error logging out instance: {e}")
            return {"status": "error", "message": str(e)}

    def fetch_profile_picture(self, jid):
        """Fetches the profile picture URL for a specific JID."""
        url = f"{self.base_url}/chat/fetchProfilePictureUrl/{self.instance_name}"
        payload = {"number": jid}
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            log_message(f"Error fetching profile picture for {jid}: {e}")
            return None

    def send_presence(self, jid, presence="composing"):
        """Sends a presence status (composing, available, etc.) to a JID."""
        url = f"{self.base_url}/chat/sendPresence/{self.instance_name}"
        payload = {
            "number": jid,
            "presence": presence
        }
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=5)
            return response.json()
        except Exception as e:
            log_message(f"Error sending presence to {jid}: {e}")
            return None

    def create_evolution_instance(self, name, token=None, number=None):
        """Creates a WhatsApp instance in Evolution API."""
        url = f"{self.base_url}/instance/create"
        payload = {
            "instanceName": name,
            "token": token or "",
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        if number:
            payload["number"] = number
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=20)
            return response.json()
        except Exception as e:
            log_message(f"Error creating evolution instance: {e}")
            return {"status": "error", "message": str(e)}

    def delete_evolution_instance(self, name):
        """Deletes a WhatsApp instance from Evolution API."""
        url = f"{self.base_url}/instance/delete/{name}"
        try:
            response = self.session.delete(url, headers=self.headers, timeout=20)
            return response.json()
        except Exception as e:
            log_message(f"Error deleting evolution instance: {e}")
            return {"status": "error", "message": str(e)}

    def set_evolution_webhook(self, name, webhook_url):
        """Sets the webhook on a WhatsApp instance in Evolution API."""
        url = f"{self.base_url}/webhook/set/{name}"
        payload = {
            "enabled": True,
            "url": webhook_url,
            "webhook_by_events": False,
            "events": [
                "APPLICATION_STARTUP",
                "QRCODE_UPDATED",
                "MESSAGES_SET",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONTACTS_SET",
                "CONTACTS_UPSERT",
                "CONTACTS_UPDATE",
                "PRESENCE_UPDATE",
                "CHATS_SET",
                "CHATS_UPSERT",
                "CHATS_UPDATE",
                "CONNECTION_UPDATE"
            ],
            "webhook": {
                "enabled": True,
                "url": webhook_url,
                "byEvents": False,
                "events": [
                    "APPLICATION_STARTUP",
                    "QRCODE_UPDATED",
                    "MESSAGES_SET",
                    "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE",
                    "SEND_MESSAGE",
                    "CONTACTS_SET",
                    "CONTACTS_UPSERT",
                    "CONTACTS_UPDATE",
                    "PRESENCE_UPDATE",
                    "CHATS_SET",
                    "CHATS_UPSERT",
                    "CHATS_UPDATE",
                    "CONNECTION_UPDATE"
                ]
            }
        }
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=15)
            return response.json()
        except Exception as e:
            log_message(f"Error setting webhook: {e}")
            return {"status": "error", "message": str(e)}
