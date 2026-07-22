from fastapi import FastAPI
import os

app = FastAPI(
    title="SikaGlé API",
    version="1.0.0",
    description="Backend officiel pour la plateforme SikaGlé"
)

def get_supabase():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if url and key:
        try:
            from supabase import create_client
            return create_client(url, key)
        except Exception as e:
            print(f"Erreur Supabase: {e}")
            return None
    return None

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Bienvenue sur l'API SikaGlé",
        "docs": "/docs"
    }

@app.get("/db-status")
def db_status():
    client = get_supabase()
    if not client:
        return {
            "database": "disconnected", 
            "reason": "Variables SUPABASE_URL ou SUPABASE_KEY manquantes"
        }
    
    try:
        response = client.table("users").select("count", count="exact").execute()
        return {
            "database": "connected",
            "status": "ok",
            "message": "Connexion à Supabase réussie !",
            "users_count": response.count
        }
    except Exception as e:
        return {
            "database": "error",
            "details": str(e)
        }
