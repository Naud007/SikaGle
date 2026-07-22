from fastapi import FastAPI

app = FastAPI(
    title="SikaGlé API",
    version="1.0.0",
    description="Backend officiel pour la plateforme SikaGlé"
)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Bienvenue sur l'API SikaGlé",
        "docs": "/docs"
    }
