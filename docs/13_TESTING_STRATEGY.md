# 13_TESTING_STRATEGY.md

# SikaGlé

# Testing Strategy

**Version :** 1.0

**Statut :** Officiel

---

# 1. Objectif

Définir la stratégie de tests utilisée pour garantir la qualité, la stabilité et la fiabilité de SikaGlé.

Cette stratégie couvre l'ensemble du cycle de développement, depuis les tests unitaires jusqu'à la validation métier des recommandations agricoles.

---

# 2. Principes

Chaque fonctionnalité développée doit être testée.

Les tests doivent permettre de vérifier :

- le bon fonctionnement du code ;
- la stabilité de l'architecture ;
- la qualité des réponses ;
- la robustesse du système ;
- les performances ;
- la sécurité.

Aucune fonctionnalité n'est considérée comme terminée sans tests.

---

# 3. Pyramide des tests

```
               Tests Manuels
                     ▲
             Tests End-to-End
                     ▲
        Tests d'Intégration
                     ▲
            Tests Unitaires
```

Les tests unitaires représentent la majorité des tests.

---

# 4. Types de tests

## 4.1 Tests Unitaires

Objectif :

Tester chaque composant indépendamment.

Exemples :

- Repository
- Service
- Provider
- Builder
- Validator
- Extractor

Objectif de couverture :

≥ 80 %

---

## 4.2 Tests d'Intégration

Objectif :

Vérifier la collaboration entre plusieurs modules.

Exemple :

```
Conversation

↓

Reasoning

↓

Knowledge

↓

Response
```

---

## 4.3 Tests End-to-End

Objectif :

Simuler une conversation complète.

Exemple :

```
Utilisateur

↓

WhatsApp

↓

Conversation

↓

Reasoning

↓

Knowledge

↓

Réponse

↓

WhatsApp
```

---

## 4.4 Tests Fonctionnels

Valider que les fonctionnalités répondent aux besoins des User Stories.

Chaque User Story possède au moins un scénario de test.

---

## 4.5 Tests Métier

Les recommandations agricoles sont comparées à des cas de référence validés par des experts.

Exemple :

Entrée :

> Les feuilles de mon maïs jaunissent.

Le moteur doit :

- demander les informations manquantes ;
- proposer plusieurs hypothèses ;
- citer ses sources ;
- éviter un diagnostic prématuré.

---

## 4.6 Tests de Performance

Mesurer :

- temps de réponse ;
- temps d'ingestion ;
- consommation mémoire ;
- utilisation CPU ;
- latence des appels LLM.

---

## 4.7 Tests de Charge

Simuler :

- plusieurs centaines d'utilisateurs ;
- plusieurs milliers de conversations ;
- pics de trafic.

---

## 4.8 Tests de Résilience

Tester :

- perte de connexion ;
- indisponibilité du LLM ;
- indisponibilité de la météo ;
- panne de ChromaDB ;
- erreur PostgreSQL.

Le système doit continuer à fonctionner de manière dégradée lorsque cela est possible.

---

## 4.9 Tests de Sécurité

Vérifier :

- authentification ;
- autorisation ;
- validation des entrées ;
- protection contre les injections ;
- limitation de débit.

---

# 5. Modules concernés

Tous les modules possèdent leurs propres tests.

```
knowledge_engine/

conversation/

reasoning/

agricultural_context/

multimodal/

integrations/

api/

core/
```

---

# 6. Jeux de données de référence

Créer un ensemble de cas agricoles représentatifs.

Exemples :

- maïs
- riz
- soja
- tomate
- manioc
- coton

Pour chaque cas :

- contexte
- symptômes
- diagnostic attendu
- recommandations attendues
- sources de référence

Ces jeux de données servent à détecter les régressions.

---

# 7. Cas de tests métier

Exemple :

## Cas 001

Culture :

Maïs

Symptôme :

Feuilles jaunes

Attendu :

- questions complémentaires ;
- hypothèses multiples ;
- recherche documentaire ;
- niveau de confiance ;
- recommandations adaptées.

---

## Cas 002

Culture :

Tomate

Symptôme :

Taches noires

Attendu :

- identification des hypothèses ;
- recherche des maladies correspondantes ;
- recommandations documentées.

---

# 8. Tests du Reasoning Engine

Le moteur de raisonnement est testé étape par étape.

```
Intent Detection

↓

Crop Detection

↓

Symptom Extraction

↓

Missing Information

↓

Hypothesis

↓

Retrieval

↓

Evidence

↓

Planning
```

Chaque étape possède ses propres tests unitaires.

---

# 9. Tests du Knowledge Engine

Vérifier :

- ingestion ;
- chunking ;
- embeddings ;
- hybrid search ;
- reranking ;
- RAG.

Les résultats doivent être :

- pertinents ;
- reproductibles ;
- traçables.

---

# 10. Tests du Conversation Engine

Tester :

- création de session ;
- reprise ;
- mémoire ;
- historique ;
- profils.

---

# 11. Tests du Multimodal Engine

Tester :

- transcription ;
- synthèse vocale ;
- détection de langue ;
- normalisation des messages.

---

# 12. Tests WhatsApp

Tester :

- réception des messages ;
- téléchargement des médias ;
- réponses ;
- reprise de conversation ;
- erreurs.

---

# 13. Critères de qualité

Avant toute livraison :

✓ tous les tests unitaires passent

✓ tous les tests d'intégration passent

✓ aucun bug critique

✓ couverture ≥ 80 %

✓ aucune régression détectée

✓ documentation mise à jour

---

# 14. Définition d'une régression

Une régression est constatée lorsque :

- une fonctionnalité existante ne fonctionne plus ;
- une réponse devient moins pertinente ;
- les performances diminuent significativement ;
- un test précédemment validé échoue.

Toute régression bloque la livraison.

---

# 15. Organisation des tests

```
tests/

unit/

integration/

functional/

e2e/

performance/

fixtures/

datasets/

utils/
```

---

# 16. Jeux de données

Créer des jeux de données dédiés pour :

- agriculture ;
- météo ;
- conversations ;
- utilisateurs ;
- documents ;
- réponses attendues.

Les jeux de données doivent être versionnés.

---

# 17. Automatisation

Les tests sont exécutés automatiquement :

- à chaque Pull Request ;
- à chaque fusion sur la branche principale ;
- avant chaque release.

Aucune version n'est publiée si les tests critiques échouent.

---

# 18. Définition de terminé

Une fonctionnalité est terminée lorsque :

- son développement est achevé ;
- les tests sont écrits ;
- les tests passent ;
- la documentation est mise à jour ;
- la revue de code est validée.

---

# 19. Indicateurs de qualité

Suivre en continu :

- couverture de code ;
- nombre de régressions ;
- temps moyen des tests ;
- taux d'échec ;
- bugs critiques ;
- disponibilité du système.

---

# 20. Vision

Les tests ne servent pas uniquement à vérifier que SikaGlé fonctionne.

Ils garantissent que les recommandations restent fiables, que les évolutions n'introduisent pas de régressions et que chaque nouvelle version améliore réellement la qualité du produit.

La stratégie de tests est un pilier essentiel de la confiance accordée à SikaGlé par ses utilisateurs.
