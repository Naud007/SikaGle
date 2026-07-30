# 🌱 SikaGlé

> **Une plateforme d'intelligence agricole alimentée par l'intelligence artificielle.**

SikaGlé est une plateforme d'intelligence agricole conçue pour accompagner les producteurs, les agronomes, les entreprises agricoles et les institutions grâce à une intelligence artificielle spécialisée.

Son objectif est de transformer les connaissances scientifiques, les données environnementales et les observations du terrain en recommandations utiles, fiables et accessibles.

---

# Vision

Mettre l'intelligence artificielle au service de chaque agriculteur africain.

Nous croyons que chaque producteur, quel que soit son niveau d'éducation ou sa localisation, doit pouvoir accéder à des conseils agricoles de qualité.

---

# Mission

SikaGlé aide les producteurs à prendre de meilleures décisions grâce à :

- une base documentaire scientifique ;
- un moteur de raisonnement agricole ;
- l'analyse du contexte (culture, météo, saison...) ;
- une assistance disponible en langage naturel.

---

# Les cinq personas

Le produit est conçu pour répondre aux besoins de cinq catégories d'utilisateurs.

## 👨🏾‍🌾 Coffi

Producteur utilisant principalement les messages vocaux et les langues locales.

---

## 👩🏾‍🌾 Aïcha

Jeune agricultrice utilisant principalement le texte.

---

## 👨🏾‍🔬 Rodrigue

Agronome, technicien ou chercheur.

---

## 🏛 Institution

Ministères, ONG, instituts de recherche, programmes agricoles.

---

## 🚜 Entrepreneur Agricole

Exploitant agricole, coopérative ou entreprise du secteur.

---

# Fonctionnalités principales

## Assistance agricole

- Questions en langage naturel
- Diagnostic assisté
- Conseils contextualisés
- Citations des sources

---

## Knowledge Engine

- Importation documentaire
- Nettoyage
- Chunking
- Embeddings
- Recherche hybride
- RAG

---

## Reasoning Engine

Avant de répondre, SikaGlé :

- identifie la culture ;
- extrait les symptômes ;
- construit des hypothèses ;
- recherche les informations pertinentes ;
- produit une réponse argumentée.

---

## Multimodal

Entrées :

- texte
- audio
- image

Sorties :

- texte
- audio

---

## Intelligence Agricole

Production d'observations anonymisées permettant :

- des statistiques ;
- des tableaux de bord ;
- des alertes ;
- des analyses territoriales.

---

# Architecture

L'architecture repose sur plusieurs moteurs spécialisés.

```text
Utilisateur
      │
      ▼
 API Layer
      │
      ▼
Conversation Engine
      │
      ▼
Reasoning Engine
      │
      ▼
Knowledge Engine
      │
      ▼
LLM
      │
      ▼
Réponse
```

---

# Structure du projet

```text
app/

├── api/
├── analytics/
├── config/
├── conversation/
├── core/
├── dashboard/
├── integrations/
├── knowledge_engine/
├── models/
├── multimodal/
├── notifications/
├── reasoning/
├── security/
├── services/
├── storage/
├── utils/
└── weather/

docs/

├── 00_VISION.md
├── 01_PRD.md
├── 02_PERSONAS.md
├── 03_ARCHITECTURE_FONCTIONNELLE.md
├── 04_ARCHITECTURE_TECHNIQUE.md
├── 05_ROADMAP.md
├── 06_MODELE_ECONOMIQUE.md
├── 07_PRINCIPES_DE_CONCEPTION.md
├── 08_GOUVERNANCE_DES_DONNEES.md
├── 09_DECISIONS_ARCHITECTURALES.md
├── 10_GLOSSAIRE.md
```

---

# Technologies

Backend

- FastAPI
- Python 3.12+

Base de données

- PostgreSQL
- ChromaDB

Intelligence Artificielle

- Gemini
- Modèles d'embeddings
- Retrieval-Augmented Generation (RAG)

Déploiement

- Render

Interfaces

- WhatsApp Cloud API
- API REST

---

# Principes

SikaGlé est construit selon plusieurs principes fondamentaux.

- L'utilisateur avant la technologie.
- Les connaissances avant les opinions.
- Comprendre avant de répondre.
- Raisonner avant de conclure.
- La transparence.
- La protection des données.
- Une architecture modulaire.
- L'amélioration continue.

---

# Documentation

Toute la documentation du projet est disponible dans le dossier `docs/`.

Elle couvre notamment :

- la vision ;
- les besoins fonctionnels ;
- les personas ;
- l'architecture ;
- la feuille de route ;
- le modèle économique ;
- les principes de conception ;
- la gouvernance des données.

---

# Roadmap

Le développement est organisé autour de cinq grandes versions.

- **V1** — Assistant Agricole Intelligent
- **V2** — Assistant Agricole Multimodal
- **V3** — Plateforme Agricole
- **V4** — Plateforme d'Intelligence Agricole
- **V5** — Infrastructure Agricole Africaine

---

# Contribution

Les contributions doivent respecter :

- l'architecture technique ;
- les principes de conception ;
- les décisions architecturales (ADR) ;
- les conventions de développement.

Toute nouvelle fonctionnalité doit être reliée à une User Story et apporter de la valeur à au moins un des cinq personas.

---

# Licence

À définir.

---

# Notre engagement

SikaGlé n'est pas simplement un assistant conversationnel.

C'est une plateforme d'intelligence agricole qui transforme les connaissances scientifiques et les observations du terrain en décisions utiles pour les producteurs, les entreprises et les institutions.

---

> **"Nous ne développons pas des fonctionnalités. Nous résolvons les problèmes des agriculteurs."**
