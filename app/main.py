from fastapi import FastAPI, Request, Response, Query
import os

app = FastAPI(
    title="SikaGlé API",
    version="1.0.0"
)

# Jeton de vérification secret pour Meta
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "sikagle_secret_token_2026")

@app.get("/")
def root():
    return {"status": "online", "message": "API SikaGlé fonctionnelle"}

@app.get("/db-status")
def db_status():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    
    if not url or not key:
        return {"database": "disconnected", "reason": "Variables d'environnement manquantes"}
    
    try:
        from supabase import create_client
        supabase = create_client(url, key)
        response = supabase.table("users").select("count", count="exact").execute()
        return {
            "database": "connected",
            "status": "ok",
            "users_count": response.count
        }
    except Exception as e:
        return {"database": "error", "details": str(e)}

# ---------------------------------------------------------
# WEBHOOK META (WHATSAPP CLOUD API)
# ---------------------------------------------------------

# 1. Verification Endpoint (GET) requis par Meta
@app.get("/webhook")
def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return Response(content=challenge, status_code=200, media_type="text/plain")
        else:
            return Response(status_code=403)
    return Response(status_code=400)

# 2. Reception Endpoint (POST) pour recevoir les messages
@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("Notification WhatsApp reçue :", data)
    
    # On renvoie 200 OK immédiatement à Meta
    return {"status": "success"}
