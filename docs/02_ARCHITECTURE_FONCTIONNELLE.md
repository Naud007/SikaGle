02_ARCHITECTURE_FONCTIONNELLE.md

Ce document ne parle presque pas de Python.

Il répond à une seule question :

Comment fonctionne SikaGlé ?

Je le structurerais ainsi.

1. Vue générale
                    SikaGlé

                         │

        ┌────────────────┼────────────────┐

        │                │                │

  Assistant IA     Intelligence      Plateforme

   agricole          agricole         numérique
2. Les 5 personas

Nous utiliserons désormais officiellement ces cinq personas.

👨‍🌾 Persona 1 — Coffi

60 ans

Cultivateur

Ne sait pas lire

WhatsApp

Audio

Fon

Objectif :

Résoudre un problème dans son champ.

👩‍🌾 Persona 2 — Aïcha

Jeune agricultrice

Sait lire

WhatsApp

Texte

Français

Objectif :

Recevoir des conseils rapides.

👨‍🔬 Persona 3 — Rodrigue

Agronome

Chercheur

Technicien

Objectif :

Accéder aux publications.

🏢 Persona 4 — Institution

MAEP

FAO

INRAB

ONG

Objectif :

Pilotage agricole.

🚜 Persona 5 — Jeune entrepreneur agricole

Exploitant moderne

Coopérative

Grande ferme

Objectif :

Optimiser sa production.

3. Les canaux d'entrée

L'utilisateur peut utiliser :

✅ WhatsApp

✅ Application mobile (plus tard)

✅ Site web

✅ API

4. Les modes d'entrée

SikaGlé comprend :

📝 Texte

🎤 Audio

📷 Image

📍 Localisation

5. Le moteur de compréhension

Modules :

Speech To Text

↓

Détection de langue

↓

Compréhension

↓

Extraction des symptômes

↓

Extraction du contexte

↓

Construction du cas agricole
6. Le Reasoning Engine

C'est le nouveau cerveau.

Il répond :

Que cherche réellement l'utilisateur ?

Il construit :

Culture

↓

Symptômes

↓

Hypothèses

↓

Informations manquantes

↓

Recherche documentaire

↓

Météo

↓

Plan de réponse
7. Les services externes

Le moteur pourra appeler :

🌦️ météo

🗺️ GPS

📖 RAG

💬 LLM

🔊 Text To Speech

📷 Vision

8. Réponse

Formats :

texte

audio

photo annotée

PDF (institution)

9. Analytics

Toutes les conversations produisent une observation anonyme.

↓

Dashboard.

↓

Statistiques.

↓

Prévisions.

10. API

Tous les modules doivent pouvoir être utilisés indépendamment.

Par exemple.

Une autre startup pourra utiliser :

uniquement

Diagnostic agricole

sans utiliser WhatsApp.
