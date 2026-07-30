# EPIC_07_API_V1.md

# SikaGlé

# EPIC 07 — Public API V1

**Epic ID :** EPIC-07

**Version :** V1

**Statut :** À développer

**Priorité :** ★★★★☆

**Responsable :** API Layer

---

# 1. Objectif

Construire une API REST stable, documentée et indépendante de l'architecture interne de SikaGlé.

L'API constitue le point d'entrée officiel des clients.

Elle doit permettre de :

- créer des conversations ;
- envoyer des messages ;
- récupérer des réponses ;
- gérer les utilisateurs ;
- consulter les informations publiques.

L'API ne doit jamais exposer directement le fonctionnement interne du Knowledge Engine ou du Reasoning Engine.

---

# 2. Valeur métier

L'API garantit que :

- WhatsApp,
- une application mobile,
- une application web,
- des partenaires,

peuvent utiliser SikaGlé de manière identique.

Elle représente un contrat stable entre les clients et la plateforme.

---

# 3. Principes de conception

L'API est :

- orientée métier ;
- versionnée ;
- documentée ;
- sécurisée ;
- stateless ;
- cohérente ;
- extensible.

Les ressources exposées reflètent les besoins des utilisateurs, jamais les composants internes.

---

# 4. Architecture

```
Client

↓

REST API

↓

API Controllers

↓

Application Services

↓

Conversation Orchestrator

↓

Conversation Engine

↓

Agricultural Context Engine

↓

Reasoning Engine

↓

Knowledge Engine

↓

Response Builder
```

---

# 5. Organisation des routes

```
api/

v1/

chat.py

conversations.py

users.py

profiles.py

health.py

system.py
```

---

# 6. Ressources

## Conversations

Créer une conversation

Récupérer une conversation

Lister les conversations

Fermer une conversation

---

## Messages

Envoyer un message

Recevoir une réponse

Consulter l'historique

---

## Utilisateurs

Créer

Modifier

Consulter

---

## Profils

Culture principale

Langue

Localisation

Préférences

---

## Santé

Health Check

Readiness

Liveness

---

# 7. Endpoints

## Conversation

```
POST /api/v1/conversations

GET /api/v1/conversations/{id}

GET /api/v1/conversations

DELETE /api/v1/conversations/{id}
```

---

## Messages

```
POST /api/v1/conversations/{id}/messages

GET /api/v1/conversations/{id}/messages
```

---

## Chat

```
POST /api/v1/chat
```

Endpoint simplifié destiné aux intégrations rapides.

---

## Utilisateurs

```
POST /api/v1/users

GET /api/v1/users/{id}

PATCH /api/v1/users/{id}
```

---

## Profils

```
GET /api/v1/users/{id}/profile

PATCH /api/v1/users/{id}/profile
```

---

## Santé

```
GET /api/v1/health

GET /api/v1/ready

GET /api/v1/live
```

---

# 8. User Stories

## US-701

En tant que développeur,

je veux envoyer une question à SikaGlé via une API,

afin d'intégrer le service dans mon application.

---

## US-702

En tant que partenaire,

je veux gérer les conversations via une API stable,

afin d'assurer la compatibilité de mon intégration.

---

## US-703

En tant qu'administrateur,

je veux vérifier rapidement l'état du système.

---

# 9. Contrats de données

## ChatRequest

```
conversation_id

user_id

message

channel

language

attachments
```

---

## ChatResponse

```
conversation_id

message_id

response

sources

confidence

metadata
```

---

## UserProfile

```
user_id

preferred_language

location

main_crops

persona
```

---

# 10. Gestion des erreurs

Réponses normalisées.

Exemple :

```
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "...",
    "details": {}
  }
}
```

Les codes HTTP doivent être utilisés de manière cohérente :

- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 422 Unprocessable Entity
- 429 Too Many Requests
- 500 Internal Server Error

---

# 11. Sécurité

Authentification :

- JWT
- API Key (partenaires)

Autorisation :

- rôles
- permissions

Protection :

- HTTPS
- validation des entrées
- limitation du débit (Rate Limiting)
- journalisation des accès

---

# 12. Dépendances

Cette Epic dépend de :

- Conversation Engine
- Agricultural Context Engine
- Reasoning Engine
- Response Builder

Elle est utilisée par :

- WhatsApp Platform
- Application Web
- Application Mobile
- API Partenaires

---

# 13. Critères d'acceptation

L'API doit permettre de :

✓ créer une conversation

✓ envoyer un message

✓ recevoir une réponse

✓ gérer les utilisateurs

✓ gérer les profils

✓ retourner des erreurs normalisées

✓ fournir une documentation OpenAPI

✓ exposer des endpoints de supervision

---

# 14. Tests

## Unitaires

- validation des schémas
- sérialisation
- contrôleurs
- gestion des erreurs

---

## Intégration

Client

↓

API

↓

Conversation

↓

Reasoning

↓

Réponse

---

## Performance

Mesurer :

- temps de réponse
- débit maximal
- latence
- taux d'erreurs

---

# 15. Évolutions V2

- API de diagnostic
- API météo
- API observations terrain
- API analytics
- API institutions
- Webhooks sortants
- Streaming des réponses
- API GraphQL (à évaluer)

---

# 16. Définition de terminé

Cette Epic sera considérée comme terminée lorsque :

- toutes les routes V1 seront disponibles ;
- les schémas de données seront stables ;
- l'authentification et l'autorisation seront opérationnelles ;
- la documentation OpenAPI sera complète ;
- les tests automatisés seront validés ;
- les performances répondront aux objectifs fixés.

---

# 17. Vision

L'API V1 est le contrat officiel entre SikaGlé et les applications qui l'utilisent.

Elle masque toute la complexité des moteurs internes et expose des capacités métier simples, cohérentes et stables.

Son rôle est de permettre l'évolution indépendante des clients et de la plateforme tout en garantissant la compatibilité des intégrations.

api/
└── v1/
    ├── chat.py
    ├── conversations.py
    ├── users.py
    └── health.py

application/
├── chat/
│   └── chat_service.py
├── conversation/
│   └── conversation_service.py
├── profile/
│   └── profile_service.py
└── system/
    └── health_service.py

conversation/
reasoning/
knowledge_engine/
multimodal/
agricultural_context/
