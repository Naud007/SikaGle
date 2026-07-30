# 11_V1_DEVELOPMENT_PLAN.md

# SikaGlé

# Plan de Développement V1

**Version :** 1.0

**Statut :** Officiel

**Objectif :** Construire le premier Assistant Agricole Intelligent utilisable en production.

---

# 1. Objectif de V1

À la fin de la V1, un agriculteur doit pouvoir :

- envoyer un message WhatsApp ;
- écrire ou parler dans sa langue ;
- poser une question agricole ;
- recevoir une réponse fiable ;
- recevoir des conseils contextualisés ;
- recevoir les sources utilisées.

La V1 constitue le MVP officiel de SikaGlé.

---

# 2. Critères de réussite

La V1 sera considérée comme terminée lorsque :

✓ un utilisateur peut discuter avec SikaGlé sur WhatsApp

✓ les conversations sont mémorisées

✓ le moteur comprend le problème agricole

✓ le RAG fournit les connaissances

✓ la météo est prise en compte

✓ la réponse est personnalisée

✓ les réponses sont citées

✓ le système est déployé en production

---

# 3. Architecture de V1

```

Utilisateur

↓

WhatsApp

↓

API

↓

Conversation Engine

↓

Reasoning Engine

↓

Knowledge Engine

↓

Weather Engine

↓

LLM

↓

Response Builder

↓

WhatsApp

↓

Utilisateur

```

---

# 4. Développement par Epic

Le développement est organisé en huit Epics.

Chaque Epic produit une valeur métier identifiable.

---

# EPIC 1 — Knowledge Platform

## Statut

🟢 En grande partie terminé

---

## Objectif

Construire une base documentaire robuste.

---

## Fonctionnalités

- ingestion
- connecteurs
- nettoyage
- chunking
- embeddings
- vectorisation
- hybrid search
- reranking
- RAG
- repository

---

## État actuel

90 % terminé.

---

## Travaux restants

- optimisation
- nouveaux connecteurs
- amélioration des performances
- enrichissement des métadonnées

---

## Priorité

Faible

---

# EPIC 2 — Conversation Engine

## Objectif

Transformer une succession de messages en une véritable conversation.

---

## Valeur utilisateur

Le système se souvient du contexte.

---

## Features

### FE-201

Gestion des sessions

---

### FE-202

Historique

---

### FE-203

Mémoire conversationnelle

---

### FE-204

Profil utilisateur

---

### FE-205

Préférences

---

### FE-206

Langue

---

## User Stories

US-201

En tant que Coffi,

je veux reprendre une conversation,

afin de ne pas tout répéter.

---

US-202

En tant qu'Aïcha,

je veux que SikaGlé se souvienne de ma culture principale.

---

## Critères d'acceptation

- contexte conservé

- mémoire persistante

- historique consultable

---

## Priorité

★★★★★

---

# EPIC 3 — Reasoning Engine

## Objectif

Construire le cerveau agricole de SikaGlé.

---

## Features

### FE-301

Détection de culture

---

### FE-302

Extraction des symptômes

---

### FE-303

Construction du contexte

---

### FE-304

Hypothèses

---

### FE-305

Questions complémentaires

---

### FE-306

Planification de la réponse

---

## User Stories

US-301

En tant que producteur,

je veux que SikaGlé comprenne mon problème,

avant de répondre.

---

## Critères d'acceptation

- culture identifiée

- symptômes extraits

- hypothèses générées

- informations manquantes détectées

---

## Priorité

★★★★★

---

# EPIC 4 — Multimodal

## Objectif

Permettre les interactions vocales.

---

## Features

### FE-401

Speech-to-Text

---

### FE-402

Text-to-Speech

---

### FE-403

Détection de langue

---

### FE-404

Traduction interne

---

### FE-405

Analyse d'image (préparation)

---

## User Stories

US-401

En tant que Coffi,

je veux envoyer un message vocal,

afin de recevoir une réponse vocale.

---

## Priorité

★★★★★

---

# EPIC 5 — Agricultural Context

## Objectif

Ajouter le contexte agricole.

---

## Features

### FE-501

Météo

---

### FE-502

Saison

---

### FE-503

Calendrier cultural

---

### FE-504

Géolocalisation

---

### FE-505

Contexte régional

---

## User Stories

US-501

En tant que producteur,

je veux recevoir un conseil adapté à la météo.

---

## Priorité

★★★★☆

---

# EPIC 6 — WhatsApp Platform

## Objectif

Créer l'interface officielle de SikaGlé.

---

## Features

### FE-601

Webhook

---

### FE-602

Réception des messages

---

### FE-603

Envoi des réponses

---

### FE-604

Gestion des médias

---

### FE-605

Gestion des erreurs

---

## User Stories

US-601

En tant que producteur,

je veux discuter avec SikaGlé directement sur WhatsApp.

---

## Priorité

★★★★★

---

# EPIC 7 — API V1

## Objectif

Stabiliser l'API publique.

---

## Endpoints

/chat

/chat/audio

/chat/image

/weather

/profile

/conversation

/diagnostic

/search

---

## Priorité

★★★☆☆

---

# EPIC 8 — Production Ready

## Objectif

Préparer le déploiement.

---

## Features

Logs

Monitoring

Health Check

CI/CD

Docker

Tests

Documentation API

Sécurité

Sauvegardes

---

## Priorité

★★★★★

---

# 5. Ordre officiel de développement

Le développement suivra strictement cet ordre.

```

1 Knowledge Platform (finalisation)

↓

2 Conversation Engine

↓

3 Reasoning Engine

↓

4 Agricultural Context

↓

5 Multimodal

↓

6 WhatsApp

↓

7 API V1

↓

8 Production Ready

```

Aucun Epic ne pourra commencer tant que les dépendances critiques ne sont pas satisfaites.

---

# 6. Dépendances

| Epic | Dépend de |
|----------|-------------------------|
| Knowledge | Aucun |
| Conversation | API |
| Reasoning | Conversation + Knowledge |
| Agricultural Context | Reasoning |
| Multimodal | Conversation |
| WhatsApp | Conversation + Reasoning |
| API | Tous les services |
| Production | Tous les Epics |

---

# 7. Définition de terminé (Definition of Done)

Une fonctionnalité est terminée uniquement si :

✅ le code est développé

✅ les tests passent

✅ les erreurs sont gérées

✅ les logs sont présents

✅ l'API est documentée

✅ la documentation est mise à jour

✅ la revue de code est validée

---

# 8. Règles de développement

Chaque développement doit respecter :

- les Principes de Conception ;
- les ADR ;
- l'Architecture Technique ;
- la Gouvernance des Données.

Aucune fonctionnalité ne sera développée sans User Story.

---

# 9. Tableau de progression

| Epic | Progression |
|----------|-------------|
| Knowledge Platform | 🟢 90 % |
| Conversation Engine | ⚪ 0 % |
| Reasoning Engine | ⚪ 0 % |
| Agricultural Context | ⚪ 0 % |
| Multimodal | ⚪ 0 % |
| WhatsApp Platform | ⚪ 0 % |
| API V1 | 🟡 Partiel |
| Production Ready | ⚪ 0 % |

---

# 10. Vision de la V1

La V1 n'a pas pour ambition d'être une plateforme complète.

Elle a pour objectif de démontrer qu'une intelligence artificielle spécialisée peut accompagner efficacement un producteur agricole dans ses décisions quotidiennes.

Chaque développement devra renforcer cette promesse.

---

# Conclusion

Ce document constitue la feuille de route officielle du développement de la Version 1 de SikaGlé.

Il garantit que chaque fonctionnalité est développée dans un ordre cohérent, qu'elle répond à un besoin utilisateur clairement identifié et qu'elle contribue directement à la mission du projet.

La V1 doit aboutir à un assistant agricole intelligent, fiable, contextualisé et prêt à être utilisé en conditions réelles.
