# 15_DEVELOPMENT_GUIDE.md

# SikaGlé

# Development Guide

**Version :** 1.0

**Statut :** Officiel

---

# 1. Objectif

Ce document définit les standards de développement du projet SikaGlé.

Il garantit que toutes les contributions respectent les mêmes principes d'architecture, de qualité, de lisibilité et de maintenabilité.

Ce guide est applicable à tous les modules du projet.

---

# 2. Philosophie

Le développement de SikaGlé repose sur cinq principes fondamentaux.

- Simplicité
- Lisibilité
- Modularité
- Testabilité
- Évolutivité

Chaque décision technique doit respecter ces principes.

---

# 3. Architecture

Le projet suit une Clean Architecture.

```

Presentation

↓

Application

↓

Domain

↓

Infrastructure

```

Les dépendances doivent toujours pointer vers le cœur métier.

Jamais l'inverse.

---

# 4. Organisation du projet

```

backend/

api/

application/

conversation/

reasoning/

knowledge_engine/

agricultural_context/

multimodal/

integrations/

repositories/

models/

schemas/

services/

core/

tests/

docs/

```

Chaque dossier possède une responsabilité unique.

---

# 5. Responsabilités

## API

Expose les endpoints.

Aucune logique métier.

---

## Application

Orchestre les cas d'usage.

---

## Domain

Contient les règles métier.

---

## Infrastructure

Connexion aux bases de données, APIs externes, stockage, météo, WhatsApp, LLM.

---

# 6. Convention de nommage

## Classes

PascalCase

Exemple :

```

ConversationService

KnowledgeRepository

WeatherProvider

```

---

## Fonctions

snake_case

```

create_session()

detect_language()

search_documents()

```

---

## Variables

snake_case

```

conversation_id

weather_context

confidence_score

```

---

## Constantes

UPPER_CASE

```

MAX_RESULTS

DEFAULT_TIMEOUT

```

---

# 7. Modules

Chaque module suit la même structure.

```

module/

models/

schemas/

repositories/

services/

validators/

builders/

exceptions/

utils/

```

La structure doit rester homogène sur l'ensemble du projet.

---

# 8. Services

Les Services contiennent la logique métier.

Ils :

- orchestrent les opérations ;
- utilisent les repositories ;
- utilisent les providers ;
- ne connaissent pas FastAPI.

---

# 9. Repositories

Responsables de l'accès aux données.

Ils ne contiennent aucune logique métier.

---

# 10. Providers

Un Provider communique avec un système externe.

Exemples :

- Weather Provider
- LLM Provider
- WhatsApp Provider
- Embedding Provider

---

# 11. Builders

Les Builders construisent des objets complexes.

Exemple :

```

AgriculturalContextBuilder

ConversationContextBuilder

PromptBuilder

```

---

# 12. Validators

Tous les contrôles métier sont regroupés dans les Validators.

Exemple :

```

WeatherValidator

CropValidator

ConversationValidator

```

---

# 13. Exceptions

Créer des exceptions spécifiques.

Exemple :

```

KnowledgeException

ReasoningException

WeatherException

ConversationException

```

Éviter les exceptions génériques.

---

# 14. Logging

Tous les événements importants doivent être journalisés.

Niveaux :

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

Les messages doivent être explicites et structurés.

---

# 15. Gestion des erreurs

Ne jamais masquer une erreur.

Toujours :

- journaliser ;
- ajouter du contexte ;
- retourner un message clair à l'utilisateur.

---

# 16. Documentation du code

Chaque classe publique possède une documentation.

Chaque méthode complexe explique :

- son objectif ;
- ses paramètres ;
- sa valeur de retour ;
- les exceptions possibles.

---

# 17. Type Hints

Toutes les fonctions utilisent les annotations de type Python.

Exemple :

```python
def detect_crop(message: str) -> Crop:
    ...
```

---

# 18. Imports

Ordre des imports :

1. Standard Library
2. Librairies externes
3. Modules internes

Exemple :

```python
import logging

from fastapi import APIRouter

from app.services.weather import WeatherService
```

---

# 19. Dépendances

Une dépendance doit être justifiée.

Avant d'ajouter une nouvelle bibliothèque, vérifier :

- qu'elle est maintenue ;
- qu'elle est documentée ;
- qu'elle apporte une réelle valeur ;
- qu'elle ne duplique pas une dépendance existante.

---

# 20. Configuration

Aucune valeur sensible ne doit apparaître dans le code.

Utiliser :

- variables d'environnement ;
- fichiers de configuration.

---

# 21. Sécurité

Toujours :

- valider les entrées ;
- limiter les privilèges ;
- protéger les secrets ;
- éviter les injections ;
- vérifier les permissions.

---

# 22. Performance

Éviter :

- les appels inutiles au LLM ;
- les requêtes répétitives ;
- les chargements excessifs.

Privilégier :

- le cache ;
- les traitements asynchrones ;
- les requêtes optimisées.

---

# 23. Tests

Chaque nouvelle fonctionnalité doit être accompagnée de tests.

Minimum :

- tests unitaires ;
- tests d'intégration si nécessaire.

Aucun code ne peut être fusionné sans validation des tests.

---

# 24. Documentation

Toute modification importante doit entraîner une mise à jour :

- du PRD ;
- des Epics concernés ;
- de la documentation technique si nécessaire.

---

# 25. Git

Une branche = une fonctionnalité.

Exemple :

```

feature/reasoning-engine

feature/weather-context

feature/audio-processing

```

---

# 26. Messages de commit

Format recommandé :

```

feat:

fix:

refactor:

docs:

test:

perf:

chore:

```

Exemples :

```

feat(conversation): add session memory

fix(reasoning): improve hypothesis selection

docs(api): update endpoints

```

---

# 27. Revue de code

Avant toute fusion, vérifier :

- lisibilité ;
- simplicité ;
- couverture de tests ;
- documentation ;
- respect de l'architecture.

---

# 28. Définition de terminé

Une fonctionnalité est terminée lorsque :

- le code est propre ;
- les tests passent ;
- la documentation est à jour ;
- la revue de code est validée ;
- les critères d'acceptation sont satisfaits.

---

# 29. Anti-patterns

À éviter :

- classes "God Object" ;
- duplication de code ;
- logique métier dans les contrôleurs ;
- dépendances circulaires ;
- méthodes trop longues ;
- variables globales ;
- fonctions avec trop de responsabilités.

---

# 30. Check-list avant Pull Request

## Architecture

- [ ] Respect des couches
- [ ] Responsabilité unique
- [ ] Pas de dépendance circulaire

## Code

- [ ] Lisible
- [ ] Typé
- [ ] Documenté

## Qualité

- [ ] Tests ajoutés
- [ ] Lint réussi
- [ ] Aucune régression

## Documentation

- [ ] Mise à jour si nécessaire

---

# 31. Vision

Le code de SikaGlé doit rester compréhensible, maintenable et évolutif.

Chaque contribution doit améliorer le produit sans compromettre sa qualité.

L'objectif n'est pas seulement de développer rapidement, mais de construire une plateforme d'intelligence agricole durable, capable d'évoluer pendant de nombreuses années.
