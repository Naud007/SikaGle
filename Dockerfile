FROM python:3.10-slim

# Installation des dépendances système (FFmpeg pour l'audio)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le code de l'application
COPY . .

# Port exposé pour l'API
EXPOSE 7860

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
