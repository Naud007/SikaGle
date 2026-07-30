# EPIC_02_CONVERSATION_ENGINE.md

# SikaGlé

# EPIC 02 — Conversation Engine

**Epic ID :** EPIC-02

**Version :** V1

**Statut :** À développer

**Priorité :** ★★★★★ (Critique)

**Responsable :** Conversation Engine

---

# 1. Objectif

Construire un moteur de conversation capable de gérer des échanges naturels entre un utilisateur et SikaGlé.

Contrairement à un chatbot classique, le Conversation Engine ne se contente pas de transmettre les messages au modèle de langage.

Il est responsable de :

- comprendre le contexte conversationnel ;
- mémoriser les informations importantes ;
- construire le contexte transmis au moteur de raisonnement ;
- gérer les profils utilisateurs ;
- maintenir la continuité des échanges.

Le Conversation Engine constitue la porte d'entrée de toute l'intelligence de SikaGlé.

---

# 2. Valeur métier

Le Conversation Engine permet à SikaGlé de tenir une véritable conversation.

Sans lui :

- chaque message est traité indépendamment ;
- le système oublie tout ;
- les utilisateurs doivent répéter les mêmes informations.

Avec lui :

- la conversation devient naturelle ;
- les réponses sont contextualisées ;
- le moteur de raisonnement reçoit toutes les informations nécessaires.

---

# 3. Personas concernés

Tous les personas utilisent le Conversation Engine.

- Coffi
- Aïcha
- Rodrigue
- Institution
- Entrepreneur Agricole

---

# 4. Architecture

```
Utilisateur

↓

Canal (WhatsApp / Web / API)

↓

Conversation Manager

↓

Session Manager

↓

Context Manager

↓

Memory Manager

↓

Profile Manager

↓

Language Manager

↓

Reasoning Engine
```

---

# 5. Structure du module

```
conversation/

models/

services/

repositories/

memory/

sessions/

context/

profiles/

languages/

history/

builders/
```

---

# 6. Responsabilités

Le Conversation Engine est responsable de :

- gérer les conversations ;
- identifier l'utilisateur ;
- ouvrir une session ;
- restaurer une session ;
- mémoriser le contexte ;
- construire le contexte courant ;
- fournir le contexte au Reasoning Engine.

Il ne produit jamais directement de réponse.

---

# 7. Fonctionnalités

---

## FE-201 — Session Manager

### Objectif

Créer et gérer les sessions de conversation.

Chaque utilisateur possède une session active.

Fonctions :

- ouverture ;
- fermeture ;
- expiration ;
- reprise.

---

## FE-202 — Conversation History

Historique complet des échanges.

Chaque message est enregistré.

Exemple :

Utilisateur

↓

Assistant

↓

Utilisateur

↓

Assistant

---

## FE-203 — Memory Manager

Gestion de la mémoire conversationnelle.

La mémoire contient uniquement les informations utiles.

Exemple :

- culture principale ;
- symptômes déjà décrits ;
- langue ;
- commune ;
- objectif de la conversation.

La mémoire ne stocke pas inutilement toute la conversation.

---

## FE-204 — Context Builder

Construit le contexte envoyé au moteur de raisonnement.

Le contexte peut contenir :

- mémoire
- historique récent
- profil
- météo
- informations utilisateur

---

## FE-205 — Profile Manager

Gestion du profil utilisateur.

Exemples :

- nom
- langue
- culture principale
- localisation
- type d'exploitation

Ces informations permettent de personnaliser les réponses.

---

## FE-206 — Language Manager

Détection de la langue.

Gestion :

- français
- fon
- yoruba
- autres langues futures

Le moteur choisit automatiquement la langue de réponse.

---

## FE-207 — Conversation State

Le moteur sait où se trouve l'utilisateur dans la conversation.

Exemple :

```
Début

↓

Identification de la culture

↓

Description des symptômes

↓

Questions complémentaires

↓

Recherche

↓

Diagnostic

↓

Conseils
```

---

## FE-208 — Context Compression

Les LLM possèdent une fenêtre de contexte limitée.

Le Conversation Engine doit :

- résumer les anciens échanges ;
- conserver uniquement les informations importantes ;
- réduire la taille des prompts.

---

## FE-209 — Conversation Policies

Gestion des règles conversationnelles.

Exemple :

- éviter les répétitions ;
- ne pas poser deux fois la même question ;
- savoir conclure une conversation.

---

# 8. User Stories

---

## US-201

En tant que Coffi,

je veux reprendre une conversation interrompue,

afin de ne pas tout réexpliquer.

---

## US-202

En tant qu'Aïcha,

je veux que SikaGlé se souvienne que je cultive principalement le maïs,

afin d'obtenir des conseils plus pertinents.

---

## US-203

En tant que Rodrigue,

je veux consulter l'historique d'une conversation,

afin d'analyser les recommandations proposées.

---

## US-204

En tant qu'utilisateur,

je veux recevoir une réponse dans la langue utilisée,

afin de mieux comprendre les recommandations.

---

# 9. Modèle conceptuel

```
User

↓

Conversation

↓

Session

↓

Messages

↓

Memory

↓

Context

↓

Reasoning
```

---

# 10. Dépendances

Cette Epic dépend de :

- API
- Knowledge Platform

Elle est nécessaire pour :

- Reasoning Engine
- WhatsApp
- Multimodal
- Weather
- Analytics

---

# 11. Données gérées

## Conversation

- id
- utilisateur
- date
- statut

---

## Message

- auteur
- contenu
- type
- date

---

## Session

- id
- utilisateur
- expiration
- statut

---

## Mémoire

- culture
- symptômes
- langue
- localisation
- préférences

---

## Profil

- persona
- langue
- région
- cultures principales

---

# 12. Critères d'acceptation

Le système doit être capable de :

✓ créer une conversation

✓ reprendre une conversation

✓ conserver le contexte

✓ conserver la mémoire

✓ identifier la langue

✓ construire le contexte

✓ transmettre le contexte au Reasoning Engine

✓ gérer plusieurs utilisateurs simultanément

---

# 13. Tests

## Unitaires

- Session Manager

- Memory Manager

- Context Builder

- Language Manager

- Profile Manager

---

## Intégration

Conversation complète.

Création

↓

Messages

↓

Mémoire

↓

Contexte

↓

Reasoning

---

## Charge

Simuler plusieurs milliers de conversations simultanées.

---

# 14. Sécurité

Le Conversation Engine doit respecter les principes de gouvernance des données.

Les conversations :

- sont protégées ;
- sont journalisées ;
- peuvent être supprimées à la demande de l'utilisateur lorsque cela est applicable.

Les observations anonymisées sont extraites séparément par les modules dédiés.

---

# 15. Travaux techniques

Création des modèles :

- Conversation
- Session
- Message
- Memory
- UserProfile

Création des services :

- ConversationService
- SessionService
- MemoryService
- ContextService
- LanguageService
- ProfileService

Création des repositories :

- ConversationRepository
- SessionRepository
- MemoryRepository

Création des API :

- création de conversation
- récupération
- historique
- suppression
- profil

---

# 16. Évolutions V2

- mémoire longue durée ;
- résumé automatique des conversations ;
- personnalisation avancée ;
- préférences intelligentes ;
- synchronisation multi-appareils ;
- recommandations proactives.

---

# 17. Définition de terminé

Cette Epic sera terminée lorsque :

- plusieurs conversations pourront être gérées simultanément ;
- le contexte sera automatiquement reconstruit ;
- la mémoire conversationnelle fonctionnera ;
- les profils utilisateurs seront persistants ;
- le moteur de raisonnement recevra un contexte complet ;
- tous les tests seront validés.

---

# Conclusion

Le Conversation Engine est le cœur relationnel de SikaGlé.

Il transforme une succession de messages indépendants en une conversation cohérente, contextualisée et personnalisée.

En assurant la gestion des sessions, de la mémoire, du contexte et des profils, il prépare les informations nécessaires au Reasoning Engine et permet à SikaGlé d'offrir une expérience utilisateur fluide, naturelle et adaptée aux besoins de chaque persona.



Utilisateur
        │
        ▼
Conversation Engine
        │
        ├────────► Memory
        │
        ├────────► User Profile
        │
        ├────────► Weather Context
        │
        ├────────► Knowledge Engine
        │
        ├────────► Reasoning Engine
        │
        └────────► Response Builder
