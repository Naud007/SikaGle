PRODUCT REQUIREMENTS DOCUMENT (PRD)
SikaGlé

Version : 1.0

Statut : Vision Produit

1. Présentation
Nom

SikaGlé

Mission

Permettre à tout acteur du monde agricole d'obtenir rapidement des conseils agricoles fiables, contextualisés et accessibles dans sa langue, grâce à l'intelligence artificielle.

2. Vision

SikaGlé ambitionne de devenir le premier assistant agricole intelligent d'Afrique de l'Ouest.

Il devra être capable de :

comprendre les langues locales ;
raisonner comme un conseiller agricole ;
s'appuyer sur des sources scientifiques fiables ;
produire des statistiques agricoles anonymisées ;
assister aussi bien les producteurs que les institutions.
3. Les utilisateurs
Persona 1 — Coffi
Profil
60 ans
Cultivateur
Zogbodomey
Téléphone Android d'entrée de gamme
Utilise WhatsApp
Ne sait ni lire ni écrire
Ses besoins
parler
écouter
comprendre
Utilisation

🎤

"SikaGlé..."

Réponse audio en fon.

Persona 2 — Aïcha
Profil
27 ans
Jeune maraîchère
Sait lire
Utilise WhatsApp
Écrit facilement

Elle écrit :

Mes tomates ont des taches noires.

SikaGlé répond en texte.

Elle peut demander :

Explique davantage.

Persona 3 — Rodrigue
Profil
Ingénieur agronome

Il demande :

Donne-moi les publications les plus récentes sur la chenille légionnaire.

Il veut :

références
sources
détails
Persona 4 — Institution

Par exemple :

Le MAEP.

Il veut :

tableaux de bord
tendances
statistiques
alertes
4. Le problème

Aujourd'hui :

Les producteurs n'ont pas toujours accès à un conseiller agricole.

Ils consultent :

trop tard ;
difficilement ;
ou se fient à des conseils non vérifiés.
5. La solution

SikaGlé devient un conseiller agricole disponible 24h/24.

Il comprend :

la voix
le texte
les photos

Il répond :

dans la langue du producteur ;
avec des sources fiables ;
avec des conseils adaptés au contexte.
6. Les fonctionnalités principales
Compréhension

Entrées :

texte
voix
photo
Raisonnement

Détection :

culture
symptômes
maladies possibles
ravageurs
contexte
Recherche documentaire

Recherche dans :

INRAB
BRAB
AfricaRice
IITA
etc.
Météo

Conseils tenant compte :

pluie
vent
température
humidité
Réponse

Formats :

texte
audio

Langues :

Français
Fon
Yoruba
Bariba
Dendi
Adja
7. Cas d'utilisation
Cas 1

Coffi.

Message vocal.

↓

Diagnostic.

↓

Réponse audio.

Cas 2

Jeune agriculteur.

Message texte.

↓

Réponse texte.

↓

Références.

Cas 3

Photo.

↓

Analyse.

↓

Question complémentaire.

↓

Diagnostic.

Cas 4

Institution.

↓

Dashboard.

↓

Statistiques.

8. Intelligence Agricole

Chaque interaction produit une observation anonyme.

Par exemple :

{
  "culture": "manioc",
  "commune": "Zogbodomey",
  "symptoms": [
    "feuilles jaunes"
  ],
  "language": "fon"
}

Jamais :

numéro de téléphone ;
nom ;
message brut sans nécessité.
9. Les règles de SikaGlé

Toujours :

✔ expliquer

✔ rassurer

✔ citer ses sources

✔ proposer une action

✔ demander des précisions si nécessaire

Jamais :

❌ inventer

❌ donner un traitement dangereux

❌ affirmer sans preuve

10. Les principes de conception

Nous adopterons une approche "Human First".

Cela signifie :

Le meilleur algorithme n'est pas celui qui est le plus complexe.

Le meilleur algorithme est celui qui aide réellement le producteur.

11. Les indicateurs de succès
Utilisation
Nombre d'agriculteurs actifs.
Nombre de conversations par jour.
Nombre de communes couvertes.
Qualité
Temps moyen de réponse.
Taux de compréhension des demandes.
Satisfaction des utilisateurs.
Impact
Nombre de problèmes résolus.
Temps gagné pour les producteurs.
Nombre d'alertes précoces générées.
Plateforme
Nombre de coopératives utilisant SikaGlé.
Nombre d'institutions clientes.
Nombre de rapports générés.
12. Notre devise

Je pense qu'un grand produit a toujours une phrase qui guide toutes les décisions.

Je proposerais :

"Chaque agriculteur mérite un conseiller agricole fiable, dans sa langue, au moment où il en a besoin."

Ou encore, une version plus ambitieuse :

"Mettre l'intelligence artificielle au service de chaque agriculteur africain."

Une dernière proposition

Je pense qu'il manque un cinquième persona, et il sera très important.

👩‍🌾 Persona 5 — Les jeunes entrepreneurs agricoles

Exemple :

24 à 40 ans ;
utilisent WhatsApp, Facebook, TikTok ;
savent lire et écrire ;
gèrent parfois plusieurs hectares ou une exploitation moderne.

Leurs besoins vont au-delà du diagnostic :

"Quel est le meilleur moment pour semer avec la météo de cette semaine ?"
"Quel est le prix actuel du maïs à Bohicon ?"
"Fais-moi un calendrier de fertilisation."
"Aide-moi à préparer un dossier de financement."
"Calcule la quantité d'engrais nécessaire pour 3,5 hectares."

Ce sont eux qui adopteront rapidement les fonctionnalités avancées et pourront devenir les premiers abonnés à une offre Premium.
