# Conventions de développement

Version : 1.0

---

# Objectif

Ce document définit les conventions de développement du projet SikaGlé.

Toutes les nouvelles fonctionnalités doivent respecter ces règles afin de garantir :

- la cohérence du code ;
- la maintenabilité ;
- la lisibilité ;
- la qualité.

---

# Structure des dossiers

Chaque dossier représente un domaine fonctionnel.

Exemple :

knowledge_engine/

    connectors/
    downloader/
    extraction/
    processing/
    validation/
    embeddings/
    vectorstore/
    retrieval/
    prompting/
    ingestion/

Chaque dossier ne doit contenir qu'une seule responsabilité.

---

# Une classe = une responsabilité

Une classe doit avoir un seul objectif.

Exemple :

✓ PDFExtractor

→ extrait le texte

✓ Downloader

→ télécharge un fichier

✓ DocumentValidator

→ valide un document

Une classe ne doit jamais faire plusieurs métiers.

---

# Une méthode = une action

Une méthode réalise une seule opération.

Exemple :

extract()

download()

validate()

index_pdf()

Éviter les méthodes qui font plusieurs traitements.

---

# Typage

Tout le code doit être typé.

Exemple :

```python
def process(
    pdf_path: Path,
) -> ProcessingResult:
```

Éviter les types implicites.

---

# Dataclasses et modèles

Les échanges entre composants utilisent des objets métier.

À privilégier :

- DocumentMetadata
- ValidationResult
- ProcessingResult
- IngestionReport

Éviter les dictionnaires lorsque la structure est stable.

---

# Gestion des erreurs

Les erreurs doivent être explicites.

Préférer :

```python
raise DocumentDownloadError(...)
```

à

```python
raise Exception(...)
```

Les exceptions génériques sont interdites.

---

# Journalisation

Ne jamais utiliser :

```python
print(...)
```

Utiliser le système de journalisation du projet.

Chaque message doit préciser :

- le composant ;
- l'action ;
- le niveau (INFO, WARNING, ERROR).

---

# Nommage

Classes

PascalCase

Exemple :

KnowledgeIndexer

DocumentProcessor

DocumentValidator

---

Méthodes

snake_case

Exemple :

index_pdf()

build_prompt()

generate_embedding()

---

Variables

snake_case

Exemple :

document_metadata

collection_size

download_path

---

Constantes

MAJUSCULES

Exemple :

DEFAULT_CHUNK_SIZE

MAX_RETRIES

---

Commentaires

Les commentaires expliquent le "pourquoi", pas le "comment".

À éviter :

```python
# incrémente i
i += 1
```

Préférer :

```python
# Ignore les documents déjà indexés
```

Le code doit être suffisamment clair pour se passer de commentaires inutiles.

---

Imports

Toujours regroupés dans cet ordre :

1. Bibliothèque standard
2. Dépendances externes
3. Modules du projet

Exemple :

```python
from pathlib import Path

from fastapi import APIRouter

from app.services.knowledge_service import KnowledgeService
```

---

Fonctions longues

Une méthode ne devrait pas dépasser environ 40 lignes.

Si une méthode devient trop longue :

extraire une méthode privée.

---

Retour des méthodes

Éviter les retours multiples lorsque cela nuit à la lisibilité.

Préférer des objets métier.

---

Tests

Chaque nouveau module doit être accompagné de tests.

Structure :

tests/

    unit/
    integration/

---

Documentation

Chaque classe possède une docstring.

Chaque méthode publique possède une docstring.

---

Architecture

Les dépendances vont toujours vers les couches inférieures.

API

↓

Services

↓

Ingestion

↓

Connecteurs

Jamais l'inverse.

---

Évolutivité

Toute nouvelle fonctionnalité doit répondre à la question :

"Peut-on ajouter une nouvelle source documentaire sans modifier le cœur du système ?"

Si la réponse est non, l'architecture doit être revue.

---

Principe SOLID

Le projet suit les principes SOLID :

- Responsabilité unique (SRP)
- Ouvert/Fermé (OCP)
- Substitution de Liskov (LSP)
- Ségrégation des interfaces (ISP)
- Inversion des dépendances (DIP)

---

Qualité du code

Avant toute fusion :

✓ Le code est typé.

✓ Les tests passent.

✓ Les docstrings sont présentes.

✓ Les imports sont ordonnés.

✓ Aucune duplication.

✓ Aucun print().

✓ Aucun TODO oublié.

✓ Aucun code mort.

---

Philosophie

Le code est écrit pour être relu.

La lisibilité est prioritaire sur l'optimisation prématurée.

Un code simple est préférable à un code ingénieux mais difficile à maintenir.
