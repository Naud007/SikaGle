from fastapi import FastAPI, Request, Response
from supabase import create_client, Client
import os

app = FastAPI(title="SikaGlé API", version="1.0.0")

# Variables d'environnement
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "sikagle_secret_token_2026")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Initialisation du client Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Erreur initialisation Supabase:", e)

@app.get("/")
def root():
    return {"status": "online", "message": "API SikaGlé fonctionnelle"}

@app.get("/db-status")
def db_status():
    if not supabase:
        return {"database": "disconnected", "reason": "Variables Supabase manquantes"}
    try:
        response = supabase.table("users").select("count", count="exact").execute()
        return {"database": "connected", "status": "ok", "users_count": response.count}
    except Exception as e:
        return {"database": "error", "details": str(e)}

# ---------------------------------------------------------
# WEBHOOK META (VERIFICATION & TRAITEMENT)
# ---------------------------------------------------------

@app.get("/webhook")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return Response(content=str(challenge), media_type="text/plain", status_code=200)
    
    return Response(content="Verification failed", status_code=403)

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("Notification WhatsApp reçue :", data)

    try:
        entries = data.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                contacts = value.get("contacts", [])

                if messages and supabase:
                    msg = messages[0]
                    sender_phone = msg.get("from")
                    msg_type = msg.get("type", "text")
                    
                    # Nom du contact dans WhatsApp
                    sender_name = contacts[0].get("profile", {}).get("name") if contacts else "Inconnu"

                    # Extrait le contenu du message
                    content = ""
                    if msg_type == "text":
                        content = msg.get("text", {}).get("body", "")
                    elif msg_type in ["image", "audio", "voice", "document"]:
                        content = f"[{msg_type.upper()}] ID: " + msg.get(msg_type, {}).get("id", "")

                    # 1. Obtenir ou créer l'utilisateur (colonne full_name)
                    user_res = supabase.table("users").select("id").eq("phone_number", sender_phone).execute()
                    
                    if user_res.data:
                        user_id = user_res.data[0]["id"]
                    else:
                        new_user = supabase.table("users").insert({
                            "phone_number": sender_phone,
                            "full_name": sender_name
                        }).execute()
                        user_id = new_user.data[0]["id"]

                    # 2. Enregistrer le message
                    supabase.table("messages").insert({
                        "user_id": user_id,
                        "message_type": msg_type,
                        "content": content
                    }).execute()
                    print(f"✅ Message enregistré avec succès pour l'utilisateur ID: {user_id}")

    except Exception as e:
        print("❌ Erreur lors du traitement du message :", str(e))

    return {"status": "success"}
