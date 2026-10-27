#!/usr/bin/env bash
# Réécrit les issues du backlog avec des formulations plus simples.
# Peut être relancé sans risque : il remplace le titre et la description, rien d'autre.
# À lancer une seule fois : bash scripts/simplifier_issues.sh
set -euo pipefail
REPO="aerosafe-ipsa/aerosafe"

# e <numéro> <priorité> <points> <titre> <objectif> <critères>
e() {
  local body
  body=$(printf '**Objectif**\n\n%s\n\n**Critères de validation**\n\n%b\n\n**Priorité** : %s · %s point(s)\n' "$5" "$6" "$2" "$3")
  gh issue edit "$1" --repo "$REPO" --title "$4" --body "$body" >/dev/null
  echo "#$1  $4"
}

e 2 Must 3 "Rédiger le cahier des charges V1" \
  "Nous souhaitons rédiger une première version du cahier des charges, afin que toute l'équipe ait la même compréhension du sujet." \
  "- [x] Contexte, objectifs, profils et fonctionnalités principales\n- [x] Exigences non fonctionnelles"
e 3 Must 5 "Rédiger le cahier des charges V2" \
  "Nous souhaitons une version qui suit le plan vu en cours, avec un périmètre précis et la description des écrans." \
  "- [x] Ce qui est inclus / exclu\n- [x] Besoins fonctionnels et non fonctionnels\n- [x] Description des écrans"
e 4 Must 2 "Définir les seuils des règles R1 à R5" \
  "Nous souhaitons fixer une valeur chiffrée pour chaque règle de détection, afin de pouvoir les coder et les tester." \
  "- [x] Un seuil par règle (5 min, 10 min, altitude, vitesse, cap)\n- [x] Seuils intégrés au cahier des charges V2"
e 5 Must 2 "Faire le diagramme de cas d'utilisation" \
  "Nous souhaitons représenter les acteurs de l'application (utilisateur, superviseur, OpenSky) et ce que chacun peut faire." \
  "- [x] Les 3 acteurs\n- [x] Les liens vers les règles et les alertes"
e 6 Must 2 "Créer un premier dépôt et tester l'API OpenSky" \
  "Nous souhaitons disposer d'un dépôt commun et vérifier que nous arrivons à récupérer des données depuis OpenSky." \
  "- [x] Dépôt créé (tovkadosh/aerosafe, archivé depuis)\n- [x] Un appel à l'API marche sur la France"
e 7 Must 1 "Créer l'organisation GitHub et le nouveau dépôt" \
  "Nous avons décidé de repartir sur un dépôt public dans une organisation, pour pouvoir protéger main et permettre au Scrum Master de gérer les réglages." \
  "- [x] Organisation aerosafe-ipsa créée\n- [x] Dépôt public + premier commit\n- [x] Ancien dépôt archivé"
e 8 Must 3 "Mettre en place Scrum sur GitHub" \
  "Nous souhaitons suivre tout notre travail sur GitHub : backlog, sprints et pull requests." \
  "- [ ] Dossier docs/scrum (rôles, méthode, comptes rendus)\n- [ ] Modèles d'issue et de PR\n- [ ] Issues et milestones créés\n- [ ] Tableau Projects"
e 9 Must 1 "Protéger la branche main" \
  "Nous souhaitons qu'aucune modification n'arrive sur main sans passer par une pull request relue par un autre membre." \
  "- [ ] Règle activée (PR + 1 validation)\n- [ ] Testé : un push direct est refusé"
e 10 Must 1 "Remettre le script de test OpenSky dans le nouveau dépôt" \
  "Nous souhaitons récupérer le script de test du sprint 2 dans le nouveau dépôt, pour qu'il serve de base au collecteur." \
  "- [ ] ingestion/test_opensky.py et requirements.txt ajoutés\n- [ ] Le script se lance sans erreur"
e 11 Must 5 "Cahier des charges V3 (version finale)" \
  "Nous souhaitons produire la version finale du cahier des charges, à rendre le 1er décembre." \
  "- [ ] Seuil R3 corrigé\n- [ ] Plus de parties « à définir »\n- [ ] Diagrammes UML, architecture, base de données, choix techniques\n- [ ] Partie Scrum"
e 12 Must 3 "Diagramme de classes et diagramme de séquence" \
  "Nous souhaitons définir les classes avant de coder, pour que le projet soit bien structuré en programmation orientée objet." \
  "- [ ] Classes du collecteur, des règles et de la base\n- [ ] Séquence : collecte → règles → alerte\n- [ ] Diagrammes dans docs/conception"
e 13 Must 3 "Maquettes des écrans" \
  "Nous souhaitons dessiner les écrans de l'application avant de commencer à les développer." \
  "- [ ] Connexion, recherche, fiche avion, dashboard\n- [ ] Images dans docs/conception/maquettes"
e 14 Must 3 "Structure du projet + PostgreSQL avec Docker" \
  "Nous souhaitons que chaque membre puisse lancer la base de données de la même façon, avec une seule commande." \
  "- [ ] docker-compose.yml avec PostgreSQL\n- [ ] Dossiers backend, collector, frontend, tests\n- [ ] README à jour"
e 15 Must 5 "Récupérer les avions sur OpenSky toutes les minutes" \
  "Nous souhaitons interroger OpenSky toutes les minutes pour disposer de données à jour sur la France." \
  "- [ ] Classe OpenSkyClient (connexion OAuth2)\n- [ ] Appel toutes les 60 s\n- [ ] Gérer les erreurs (quota dépassé, valeurs vides)\n- [ ] Tests\n- [ ] Remplace le script de test"
e 16 Must 3 "Enregistrer l'historique des positions en base" \
  "Nous souhaitons conserver toutes les positions reçues, pour reconstruire les trajets et comparer deux instants." \
  "- [ ] Tables aircraft et observation\n- [ ] Index sur (icao24, date)\n- [ ] Pas de doublons"
e 17 Must 2 "Données de secours pour la démo" \
  "Nous souhaitons enregistrer des données à l'avance, pour que la démonstration fonctionne même si OpenSky ne répond pas." \
  "- [ ] Quelques heures de données sauvegardées\n- [ ] Script pour les charger en base"
e 18 Must 5 "Connexion avec un rôle (utilisateur / superviseur)" \
  "Nous souhaitons que chaque personne se connecte et n'accède qu'aux fonctionnalités de son profil." \
  "- [ ] Mots de passe chiffrés (bcrypt)\n- [ ] Jeton JWT\n- [ ] Un utilisateur n'a pas accès aux pages superviseur"
e 19 Must 2 "Tests automatiques à chaque PR (CI)" \
  "Nous souhaitons que GitHub vérifie automatiquement le code à chaque pull request, pour ne jamais fusionner du code qui ne fonctionne pas." \
  "- [ ] GitHub Actions : ruff + pytest\n- [ ] La PR est bloquée si ça échoue\n- [ ] Badge dans le README"
e 20 Must 5 "Moteur de règles + règles R1 et R2" \
  "Nous souhaitons détecter les avions qui ne donnent plus de nouvelles." \
  "- [ ] Classe Rule (abstraite) et classe RuleEngine\n- [ ] R1 : plus de 5 min sans contact\n- [ ] R2 : position vieille de plus de 10 min\n- [ ] Tests"
e 21 Must 3 "Règles R3, R4 et R5" \
  "Nous souhaitons détecter les changements brusques d'altitude, de vitesse ou de cap." \
  "- [ ] R3 : plus de 15 m/s en vertical\n- [ ] R4 : plus de 51 m/s d'écart en moins de 60 s\n- [ ] R5 : plus de 45° en moins de 60 s (attention au passage 350° → 10°)\n- [ ] Tests"
e 22 Must 3 "Enregistrer les alertes" \
  "Nous souhaitons conserver chaque alerte avec l'explication de son déclenchement." \
  "- [ ] Avion, règle, date, valeur, seuil, message\n- [ ] Pas d'alerte en double"
e 23 Must 3 "API : rechercher un avion" \
  "Nous souhaitons pouvoir rechercher un avion par son code ICAO24 ou par son indicatif." \
  "- [ ] GET /aircraft?q=\n- [ ] GET /aircraft/{icao24}\n- [ ] Tests"
e 24 Must 2 "API : trajet d'un avion" \
  "Nous souhaitons récupérer les positions successives d'un avion pour tracer son trajet." \
  "- [ ] GET /aircraft/{icao24}/trajectory\n- [ ] Positions triées par date"
e 25 Must 2 "Page de connexion" \
  "Nous souhaitons une page de connexion simple qui redirige chaque personne vers la bonne page selon son rôle." \
  "- [ ] Redirection vers la recherche ou le dashboard\n- [ ] Message clair en cas d'erreur"
e 26 Must 3 "Page de recherche" \
  "Nous souhaitons que l'utilisateur puisse trouver un avion en quelques secondes." \
  "- [ ] Barre de recherche\n- [ ] Liste des résultats (code, indicatif, statut)"
e 27 Must 5 "Page d'un avion avec la carte" \
  "Nous souhaitons afficher le trajet d'un avion sur une carte, ainsi que l'évolution de son altitude, de sa vitesse et de son cap." \
  "- [ ] Carte Leaflet avec le trajet\n- [ ] Graphiques altitude, vitesse, cap\n- [ ] Alertes de l'avion"
e 28 Must 5 "Dashboard superviseur" \
  "Nous souhaitons que le superviseur voie d'un coup d'œil les avions suivis et les alertes en cours." \
  "- [ ] Nombre d'avions suivis et d'alertes\n- [ ] Tableau des alertes\n- [ ] Carte de tous les avions"
e 29 Should 3 "Modifier les seuils des règles" \
  "Nous souhaitons que le superviseur puisse modifier les seuils des règles sans toucher au code." \
  "- [ ] Seuils stockés en base\n- [ ] Page réservée au superviseur"
e 30 Should 3 "Filtrer et traiter les alertes" \
  "Nous souhaitons que le superviseur puisse filtrer les alertes et indiquer celles qu'il a traitées." \
  "- [ ] Filtres par règle, avion, date\n- [ ] Bouton « traitée »"
e 31 Must 3 "Tout lancer avec docker compose up" \
  "Nous souhaitons lancer toute l'application avec une seule commande, notamment pour la démonstration." \
  "- [ ] Base, collecteur, API et interface démarrent ensemble"
e 32 Should 2 "Documentation du code en ligne" \
  "Nous souhaitons générer une documentation du code à partir des docstrings." \
  "- [ ] Doc générée (pdoc)\n- [ ] Publiée sur GitHub Pages"
e 33 Must 1 "Version 1.0 et rendu du 1er décembre" \
  "Nous souhaitons livrer une version stable dans les temps." \
  "- [ ] Tag v1.0.0 et release\n- [ ] Mail envoyé à Mme Sboui (cahier des charges, lien GitHub, ajout comme collaboratrice)"
e 34 Must 3 "Présentation PowerPoint" \
  "Nous souhaitons préparer un support de 20 minutes pour la soutenance." \
  "- [ ] Fichier .pptx\n- [ ] Captures du tableau Scrum, des PR et des versions"
e 35 Must 2 "Préparer et répéter la démo" \
  "Nous souhaitons une démonstration de 10 minutes qui fonctionne du premier coup." \
  "- [ ] Déroulé écrit dans docs/demo.md\n- [ ] Deux répétitions\n- [ ] Plan B avec les données de secours"
e 36 Could 2 "Niveau de gravité des alertes (bonus)" \
  "Nous souhaitons que le superviseur puisse traiter en priorité les alertes les plus graves." \
  "- [ ] Gravité par règle\n- [ ] Tri par gravité"
e 37 Could 5 "Détection d'anomalies par IA (bonus)" \
  "Nous souhaitons tester une approche par intelligence artificielle pour repérer les vols atypiques, et la comparer à nos règles." \
  "- [ ] Modèle Isolation Forest entraîné sur nos données\n- [ ] Comparaison avec les alertes des règles"

echo "Issues mises à jour."
