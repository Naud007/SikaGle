from fastapi import FastAPI
import os
from supabase import create_client, Client

app = FastAPI(
    title="SikaGlé API",
    version="1.0.0",
    description="Backend officiel pour la plateforme SikaGlé"
)

# Initialisation du client Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Erreur de connexion Supabase: {e}")

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Bienvenue sur l'API SikaGlé",
        "docs": "/docs"
    }

@app.get("/db-status")
def db_status():
    if not supabase:
        return {
            "database": "disconnected", 
            "reason": "Variables SUPABASE_URL ou SUPABASE_KEY non configurées"
        }
    
    try:
        # Test de lecture de la table users
        response = supabase.table("users").select("count", count="exact").execute()
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
