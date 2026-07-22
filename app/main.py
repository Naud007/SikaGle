from fastapi import FastAPI
import os

app = FastAPI(
    title="SikaGlé API",
    version="1.0.0"
)

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
