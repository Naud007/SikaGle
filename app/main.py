from fastapi import FastAPI, Request, Response
from supabase import create_client, Client
from datetime import date, datetime
import os

app = FastAPI(title="SikaGlé API", version="1.0.0")

# Quotas quotidiens selon l'ancienneté
TRIAL_PERIOD_DAYS = 31  # Nombre de jours d'essai gratuit
TRIAL_DAILY_LIMIT = 15  # Crédits par jour pendant l'essai
REGULAR_DAILY_LIMIT = 5 # Crédits par jour après la période d'essai

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
                    msg_id = msg.get("id")
                    msg_type = msg.get("type", "text")
                    sender_name = contacts[0].get("profile", {}).get("name") if contacts else "Inconnu"

                    # Extrait le contenu du message
                    content = ""
                    if msg_type == "text":
                        content = msg.get("text", {}).get("body", "")
                    elif msg_type in ["image", "audio", "voice", "document"]:
                        content = f"[{msg_type.upper()}] ID: " + str(msg.get(msg_type, {}).get("id", ""))

                    today_date = date.today()
                    today_str = today_date.isoformat()

                    # 1. Vérifier si l'utilisateur existe
                    user_res = supabase.table("users").select("id, credits, last_active_date, created_at").eq("phone_number", sender_phone).execute()
                    
                    if user_res.data:
                        user = user_res.data[0]
                        user_id = user["id"]
                        user_credits = user.get("credits")
                        last_active = user.get("last_active_date")
                        
                        # Calcul de l'ancienneté du compte en jours
                        created_at_str = user.get("created_at")
                        if created_at_str:
                            created_at_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")).date()
                            days_old = (today_date - created_at_dt).days
                        else:
                            days_old = 0

                        # Détermination de la limite quotidienne selon l'ancienneté
                        daily_limit = TRIAL_DAILY_LIMIT if days_old <= TRIAL_PERIOD_DAYS else REGULAR_DAILY_LIMIT

                        # Réinitialisation quotidienne des crédits si changement de jour
                        if last_active != today_str:
                            user_credits = daily_limit
                        elif user_credits is None:
                            user_credits = daily_limit

                    else:
                        # Nouvel utilisateur (Période d'essai de 31 jours -> 15 crédits/jour)
                        daily_limit = TRIAL_DAILY_LIMIT
                        new_user = supabase.table("users").insert({
                            "phone_number": sender_phone,
                            "full_name": sender_name,
                            "credits": daily_limit,
                            "last_active_date": today_str
                        }).execute()
                        user_id = new_user.data[0]["id"]
                        user_credits = daily_limit

                    # 2. Vérification du quota
                    if user_credits <= 0:
                        print(f"⚠️ Utilisateur {user_id} a épuisé ses crédits du jour (Limite: {daily_limit}).")
                        continue

                    # 3. Décrémenter 1 crédit et mettre à jour la date d'activité
                    remaining_credits = user_credits - 1
                    supabase.table("users").update({
                        "credits": remaining_credits,
                        "last_active_date": today_str
                    }).eq("id", user_id).execute()

                    # 4. Enregistrer le message
                    supabase.table("messages").insert({
                        "user_id": user_id,
                        "whatsapp_message_id": msg_id,
                        "message_type": msg_type,
                        "content": content
                    }).execute()

                    print(f"✅ Message enregistré. Crédits restants pour l'utilisateur {user_id} : {remaining_credits}/{daily_limit}")

    except Exception as e:
        print("❌ Erreur lors du traitement du message :", str(e))

    return {"status": "success"}
