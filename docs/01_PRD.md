# 01_PRD.md

# SikaGlé

## Product Requirements Document (PRD)

**Version :** 1.0

**Statut :** Officiel

**Dernière mise à jour :** Juillet 2026

---

# 1. Présentation du produit

## Nom

**SikaGlé**

## Type

Plateforme d'intelligence artificielle spécialisée dans le conseil agricole.

## Description

SikaGlé est un assistant agricole intelligent capable de comprendre les demandes des utilisateurs par texte, voix ou image, d'analyser leur contexte, de consulter une base de connaissances scientifiques et de fournir des recommandations adaptées, fiables et compréhensibles.

Le produit est conçu pour être accessible aussi bien aux producteurs agricoles qu'aux jeunes entrepreneurs, aux techniciens agricoles et aux institutions.

---

# 2. Objectif du produit

L'objectif principal de SikaGlé est de rendre les connaissances agricoles accessibles à tous, indépendamment :

- du niveau d'instruction ;
- de la langue parlée ;
- de la localisation géographique ;
- de l'accès à un conseiller agricole.

Le système doit permettre d'obtenir rapidement un conseil fiable, contextualisé et compréhensible.

---

# 3. Les utilisateurs cibles

Le produit est conçu pour cinq catégories principales d'utilisateurs.

## Persona 1 — Coffi

Profil :

- Producteur agricole
- 60 ans
- Utilise WhatsApp
- Ne sait ni lire ni écrire

Entrées préférées :

- messages vocaux

Sorties préférées :

- réponses vocales

Objectif :

Recevoir rapidement un conseil pratique dans sa langue.

---

## Persona 2 — Aïcha

Profil :

- Jeune agricultrice
- Sait lire et écrire
- Utilise principalement les messages texte

Entrées :

- texte

Sorties :

- texte
- images
- tableaux

Objectif :

Recevoir des recommandations détaillées et faciles à consulter.

---

## Persona 3 — Rodrigue

Profil :

- Agronome
- Conseiller agricole
- Chercheur

Objectif :

Consulter rapidement des publications scientifiques, recommandations techniques et références documentaires.

---

## Persona 4 — Institutions

Exemples :

- MAEP
- INRAB
- FAO
- AfricaRice
- IITA
- ONG

Objectif :

Accéder à des tableaux de bord, statistiques, indicateurs et analyses.

---

## Persona 5 — Jeunes entrepreneurs agricoles

Profil :

- Exploitants modernes
- Coopératives
- Entrepreneurs agricoles

Objectif :

Optimiser la gestion de leur exploitation grâce à des outils intelligents.

---

# 4. Les problèmes à résoudre

Aujourd'hui les producteurs rencontrent plusieurs difficultés :

- manque d'accès aux conseillers agricoles ;
- difficulté à identifier rapidement les maladies ;
- manque d'informations fiables ;
- faible accès aux publications scientifiques ;
- difficultés liées au changement climatique ;
- difficultés à choisir les traitements adaptés.

SikaGlé doit réduire ces difficultés.

---

# 5. Les objectifs fonctionnels

Le système doit être capable de :

- comprendre une demande écrite ;
- comprendre un message vocal ;
- analyser une image agricole ;
- reconnaître une culture ;
- identifier des symptômes ;
- proposer plusieurs hypothèses ;
- rechercher dans une base documentaire ;
- citer ses sources ;
- tenir compte du contexte ;
- produire une réponse adaptée.

---

# 6. Les modes d'entrée

Le système devra accepter plusieurs types d'entrées.

## Texte

Exemple :

> Mes feuilles de manioc deviennent jaunes.

---

## Audio

Exemple :

Un message vocal WhatsApp en fon.

---

## Image

Exemple :

Photographie d'une feuille malade.

---

## Informations contextuelles

Lorsque disponibles :

- localisation ;
- météo ;
- saison ;
- historique ;
- culture connue.

---

# 7. Les modes de sortie

Le système devra pouvoir produire :

- texte ;
- audio ;
- images annotées ;
- rapports PDF ;
- tableaux.

---

# 8. Les principales fonctionnalités

## Compréhension

Extraction automatique de :

- culture ;
- symptômes ;
- ravageurs ;
- maladies possibles ;
- traitements déjà appliqués ;
- stade de développement.

---

## Raisonnement

Le moteur doit être capable de :

- faire plusieurs hypothèses ;
- déterminer les informations manquantes ;
- poser des questions complémentaires ;
- éviter les conclusions hâtives.

---

## Recherche documentaire

Recherche dans :

- publications scientifiques ;
- guides techniques ;
- fiches agricoles ;
- documents institutionnels.

---

## Génération de réponses

Les réponses devront être :

- compréhensibles ;
- contextualisées ;
- structurées ;
- accompagnées de références lorsque possible.

---

## Réponses multilingues

Le système devra progressivement supporter :

- Français ;
- Fon ;
- Yoruba ;
- Adja ;
- Bariba ;
- Dendi.

---

# 9. Cas d'utilisation

## Cas 1

Un producteur envoie un message vocal.

Le système :

- comprend la langue ;
- extrait les symptômes ;
- consulte les connaissances ;
- répond par audio.

---

## Cas 2

Une agricultrice écrit une question.

Le système répond en texte avec des explications détaillées.

---

## Cas 3

Un utilisateur envoie une photo.

Le système :

- analyse l'image ;
- demande éventuellement des précisions ;
- fournit un diagnostic.

---

## Cas 4

Un chercheur recherche une publication.

Le système renvoie :

- les documents pertinents ;
- les références ;
- les extraits utiles.

---

## Cas 5

Une institution consulte un tableau de bord.

Le système affiche :

- statistiques ;
- cartes ;
- tendances ;
- alertes.

---

# 10. Contraintes du produit

Le système devra :

- fonctionner sur WhatsApp ;
- rester simple à utiliser ;
- répondre rapidement ;
- être robuste face aux erreurs des utilisateurs ;
- fonctionner même avec des messages imprécis.

---

# 11. Exigences non fonctionnelles

## Performance

Temps de réponse cible :

moins de 10 secondes.

---

## Disponibilité

Objectif :

99 % de disponibilité.

---

## Fiabilité

Les réponses doivent être justifiées lorsque cela est possible.

---

## Sécurité

Les données personnelles doivent être protégées.

Les observations utilisées pour les analyses devront être anonymisées.

---

## Évolutivité

L'architecture devra permettre l'ajout futur de :

- nouvelles langues ;
- nouveaux pays ;
- nouvelles cultures ;
- nouveaux modèles d'IA ;
- nouveaux canaux de communication.

---

# 12. Fonctionnalités futures

Les versions suivantes intégreront notamment :

- mémoire utilisateur ;
- météo avancée ;
- calendrier agricole ;
- vision par ordinateur ;
- suivi d'exploitation ;
- marketplace ;
- tableaux de bord institutionnels ;
- API publique ;
- intelligence prédictive.

---

# 13. Critères de succès

Le projet sera considéré comme réussi si les utilisateurs peuvent :

- obtenir une réponse pertinente rapidement ;
- comprendre facilement les recommandations ;
- utiliser SikaGlé sans formation préalable.

Des indicateurs permettront de mesurer :

- le nombre d'utilisateurs actifs ;
- le taux de satisfaction ;
- le temps moyen de réponse ;
- le taux de compréhension des requêtes ;
- la qualité des recommandations.

---

# 14. Hors périmètre (Version 1)

Les fonctionnalités suivantes ne font pas partie de la première version :

- Marketplace agricole
- Crédit agricole
- Assurance
- Gestion complète d'exploitation
- Commerce électronique
- Réseau social
- Application mobile native
- Tableau de bord institutionnel avancé

Ces fonctionnalités seront développées dans les versions ultérieures.

---

# 15. Définition du succès

La première version de SikaGlé sera considérée comme réussie lorsqu'un producteur pourra :

1. Envoyer un message vocal ou écrit.
2. Être compris par le système.
3. Recevoir une réponse claire dans sa langue.
4. Obtenir des conseils fiables basés sur des sources scientifiques.
5. Utiliser le service sans assistance technique.

---

# Conclusion

Le Product Requirements Document constitue la référence fonctionnelle de SikaGlé.

Toutes les nouvelles fonctionnalités devront répondre à un besoin identifié dans ce document.

Toute évolution du produit devra préserver la mission première :

**mettre l'intelligence artificielle au service des producteurs agricoles tout en restant accessible, fiable et utile.**
