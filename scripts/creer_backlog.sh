#!/usr/bin/env bash
# Crée sur GitHub les labels, les milestones (sprints) et les issues (user stories)
# du backlog AeroSafe. À lancer UNE SEULE FOIS par le Product Owner.
#
# Prérequis : GitHub CLI installé (brew install gh) et connecté (gh auth login),
# avec un compte membre de l'organisation aerosafe-ipsa.
#
# Usage : bash scripts/creer_backlog.sh
set -euo pipefail

REPO="aerosafe-ipsa/aerosafe"

# Identifiants GitHub des membres (laisser vide si inconnu : l'issue sera créée sans responsable)
GH_LUCAS="lleuginer"
GH_TOV="tovkadosh"
GH_RYAN="Zilwaa974"
GH_TEDDY="teddymbatna-sketch"

read -r -p "Créer le backlog sur $REPO ? (o/N) " ok
[[ "$ok" == "o" ]] || exit 0

# ---------------------------------------------------------------- labels
label() { gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force >/dev/null; echo "label $1"; }
label "user-story"   "1f6feb" "Story du backlog produit"
label "a-posteriori" "8b949e" "Travail réalisé avant la mise en place de GitHub, tracé a posteriori"
label "must"   "d73a4a" "MoSCoW : indispensable"
label "should" "fbca04" "MoSCoW : attendu"
label "could"  "0e8a16" "MoSCoW : bonus"
for p in 1 2 3 5 8; do label "points:$p" "c5def5" "Complexité estimée"; done
label "epic:cadrage"    "5319e7" "Cahier des charges et conception"
label "epic:donnees"    "5319e7" "Collecte OpenSky et base de données"
label "epic:auth"       "5319e7" "Authentification et rôles"
label "epic:regles"     "5319e7" "Moteur de règles et alertes"
label "epic:api"        "5319e7" "API FastAPI"
label "epic:interface"  "5319e7" "Interface web"
label "epic:devops"     "5319e7" "Qualité, CI, Docker"
label "epic:ia"         "5319e7" "Module IA (bonus)"
label "epic:soutenance" "5319e7" "Présentation et démo"

# ------------------------------------------------------------ milestones
milestone() { # titre date_fin description
  gh api "repos/$REPO/milestones" -f title="$1" -f due_on="$2T22:00:00Z" -f description="$3" >/dev/null
  echo "milestone $1"
}
milestone "Sprint 0" "2026-09-27" "14 → 27 sept. — Cadrage"
milestone "Sprint 1" "2026-10-11" "28 sept. → 11 oct. — Organisation et données"
milestone "Sprint 2" "2026-10-25" "12 → 25 oct. — Premier dépôt et premier accès API"
milestone "Sprint 3" "2026-11-01" "26 oct. → 1er nov. — Mise en place Scrum et conception"
milestone "Sprint 4" "2026-11-08" "2 → 8 nov. — Collecte, base de données, authentification"
milestone "Sprint 5" "2026-11-15" "9 → 15 nov. — Moteur de règles et API"
milestone "Sprint 6" "2026-11-22" "16 → 22 nov. — Interface web"
milestone "Sprint 7" "2026-11-29" "23 → 29 nov. — Finitions et release v1.0"
milestone "Sprint 8" "2026-12-06" "30 nov. → 6 déc. — Soutenance"

# --------------------------------------------------------------- stories
# story <sprint> <responsable> <priorité> <points> <epic> <titre> <story> <critères> [open|closed|done]
#   closed : réalisé avant GitHub (label a-posteriori) ; done : réalisé aujourd'hui
story() {
  local sprint="$1" who="$2" prio="$3" pts="$4" epic="$5" title="$6" text="$7" crit="$8" state="${9:-open}"
  local body labels url
  body=$(printf '### Story\n\n%s\n\n### Critères d'"'"'acceptation\n\n%b\n\n### Priorité\n\n%s — %s points\n' "$text" "$crit" "$prio" "$pts")
  labels="user-story,$(echo "$prio" | tr '[:upper:]' '[:lower:]'),points:$pts,epic:$epic"
  if [[ "$state" == "closed" ]]; then labels="$labels,a-posteriori"; fi
  local args=(--repo "$REPO" --title "$title" --body "$body" --label "$labels" --milestone "$sprint")
  if [[ -n "$who" ]]; then args+=(--assignee "$who"); fi
  url=$(gh issue create "${args[@]}")
  echo "$url  $title"
  if [[ "$state" == "closed" ]]; then
    gh issue close "$url" --repo "$REPO" --comment "Réalisé pendant le $sprint, avant la mise en place du suivi GitHub. Voir docs/scrum/sprints/." >/dev/null
  elif [[ "$state" == "done" ]]; then
    gh issue close "$url" --repo "$REPO" --comment "Fait le 27 octobre 2026." >/dev/null
  fi
}

# Sprints 0 à 2 : travail déjà réalisé, tracé a posteriori  (#1 à #5)
story "Sprint 0" "$GH_RYAN" Must 3 cadrage "Cahier des charges V1" \
  "En tant qu'équipe, nous voulons une première expression du besoin, afin de partager la même compréhension du sujet." \
  "- [x] Contexte, objectifs et fonctionnalités décrits" closed
story "Sprint 1" "$GH_TEDDY" Must 3 cadrage "Cahier des charges V2" \
  "En tant qu'équipe, nous voulons un cahier des charges structuré par chapitres, afin de couvrir tout le besoin." \
  "- [x] Besoins, profils, règles, architecture et exigences non fonctionnelles décrits" closed
story "Sprint 1" "$GH_LUCAS" Must 5 cadrage "Cahier des charges V3" \
  "En tant que Product Owner, je veux un cahier des charges suivant le plan du cours avec des seuils chiffrés, afin de cadrer précisément le périmètre." \
  "- [x] Périmètre inclus et exclu\n- [x] Seuils des règles R1 à R5\n- [x] Maquettes décrites" closed
story "Sprint 1" "$GH_LUCAS" Must 2 cadrage "Diagramme de cas d'utilisation" \
  "En tant qu'équipe, nous voulons identifier les acteurs et les cas d'utilisation, afin de valider les fonctionnalités avec les deux profils." \
  "- [x] Acteurs Utilisateur, Superviseur et OpenSky\n- [x] Relations include vers le moteur de règles et les alertes" closed
story "Sprint 2" "$GH_TOV" Must 2 donnees "Créer un premier dépôt et tester l'API OpenSky" \
  "En tant qu'équipe, nous voulons un dépôt commun et un accès validé à OpenSky, afin de démarrer le développement." \
  "- [x] Dépôt GitHub créé (tovkadosh/aerosafe, archivé depuis)\n- [x] Appel /states/all réussi en OAuth2 sur la zone France" closed

# Sprint 3  (#6 à #13)
story "Sprint 3" "$GH_LUCAS" Must 1 devops "Créer l'organisation GitHub et le nouveau dépôt" \
  "En tant qu'équipe, nous voulons un dépôt public dans une organisation, afin de protéger main et de donner les droits d'administration au Scrum Master." \
  "- [x] Organisation aerosafe-ipsa créée, Tov propriétaire\n- [x] Dépôt public aerosafe, commit initial\n- [x] Ancien dépôt archivé" done
story "Sprint 3" "$GH_LUCAS" Must 3 devops "Mettre en place Scrum sur GitHub" \
  "En tant qu'équipe, nous voulons suivre tout notre travail sur GitHub, afin de rendre la méthode Scrum visible et vérifiable." \
  "- [ ] docs/scrum (rôles, méthode, DoD, comptes rendus)\n- [ ] Modèles d'issue et de PR\n- [ ] Backlog en issues et milestones\n- [ ] Tableau GitHub Projects"
story "Sprint 3" "$GH_TOV" Must 1 devops "Protéger la branche main" \
  "En tant que Scrum Master, je veux interdire les poussées directes sur main, afin que tout passe par une pull request relue." \
  "- [ ] Règle de protection : PR obligatoire, 1 approbation\n- [ ] Testé : un push direct sur main est refusé"
story "Sprint 3" "$GH_TOV" Must 1 donnees "Réimporter le script de test OpenSky" \
  "En tant qu'équipe, nous voulons retrouver le script de test de l'API dans le nouveau dépôt, afin de s'en servir de base pour le collecteur." \
  "- [ ] ingestion/test_opensky.py et requirements.txt présents\n- [ ] Le script s'exécute (python ingestion/test_opensky.py)"
story "Sprint 3" "$GH_LUCAS" Must 5 cadrage "Cahier des charges V4 consolidé" \
  "En tant que Product Owner, je veux une version finale du cahier des charges, afin de la rendre le 1er décembre." \
  "- [ ] Seuil R3 corrigé, unités SI\n- [ ] Plus aucune section « à définir »\n- [ ] Conception UML, architecture, modèle de données, choix techniques\n- [ ] Partie Scrum (rôles, backlog, sprints)"
story "Sprint 3" "$GH_RYAN" Must 3 cadrage "Diagrammes de classes et de séquence" \
  "En tant que développeur, je veux un diagramme de classes et un diagramme de séquence, afin de coder une architecture orientée objet cohérente." \
  "- [ ] Classes du collecteur, du moteur de règles et des modèles\n- [ ] Séquence collecte → règles → alerte\n- [ ] Diagrammes en Mermaid dans docs/conception"
story "Sprint 3" "$GH_TEDDY" Must 3 interface "Maquettes des écrans" \
  "En tant qu'utilisateur, je veux des écrans clairs, afin de trouver vite un aéronef et comprendre ses alertes." \
  "- [ ] Connexion, recherche, fiche aéronef, dashboard\n- [ ] Images dans docs/conception/maquettes"
story "Sprint 3" "$GH_TOV" Must 3 devops "Structure du projet et PostgreSQL sous Docker" \
  "En tant que développeur, je veux lancer la base de données avec une commande, afin que les quatre membres aient le même environnement." \
  "- [ ] docker-compose.yml avec PostgreSQL\n- [ ] Arborescence backend, collector, frontend, tests\n- [ ] README à jour"

# Sprint 4
story "Sprint 4" "$GH_LUCAS" Must 5 donnees "Collecter périodiquement les états OpenSky" \
  "En tant que système, je veux interroger OpenSky à intervalle régulier, afin d'avoir des observations à jour." \
  "- [ ] Classe OpenSkyClient (OAuth2, renouvellement du jeton)\n- [ ] Appel toutes les 60 s sur la zone France\n- [ ] Erreur 429 et valeurs nulles gérées\n- [ ] Tests du parsing\n- [ ] Le script de test du sprint 2 est remplacé"
story "Sprint 4" "$GH_LUCAS" Must 3 donnees "Stocker l'historique des observations" \
  "En tant que système, je veux conserver toutes les observations horodatées, afin de reconstruire les trajectoires et comparer deux instants." \
  "- [ ] Tables aircraft et observation (SQLAlchemy)\n- [ ] Index sur (icao24, observed_at)\n- [ ] Pas de doublon"
story "Sprint 4" "$GH_LUCAS" Must 2 donnees "Jeu de données de secours pour la démo" \
  "En tant qu'équipe, nous voulons des données enregistrées, afin de faire la démo même si OpenSky ne répond pas." \
  "- [ ] Plusieurs heures de données exportées\n- [ ] Script de chargement en base"
story "Sprint 4" "$GH_RYAN" Must 5 auth "Se connecter avec son rôle" \
  "En tant qu'utilisateur ou superviseur, je veux me connecter, afin d'accéder aux fonctions de mon profil." \
  "- [ ] Mots de passe hachés (bcrypt)\n- [ ] Jeton JWT\n- [ ] Routes superviseur refusées à un utilisateur (403)"
story "Sprint 4" "$GH_TOV" Must 2 devops "Intégration continue" \
  "En tant qu'équipe, nous voulons des vérifications automatiques à chaque PR, afin de ne jamais fusionner du code cassé." \
  "- [ ] GitHub Actions : ruff + pytest\n- [ ] Vérification obligatoire avant fusion\n- [ ] Badge dans le README"

# Sprint 5
story "Sprint 5" "$GH_RYAN" Must 5 regles "Moteur de règles et règles R1, R2" \
  "En tant que superviseur, je veux être alerté d'une perte de contact ou d'une position périmée, afin de repérer un aéronef qui ne donne plus de nouvelles." \
  "- [ ] Classe abstraite Rule et classe RuleEngine\n- [ ] R1 > 5 min, R2 > 10 min\n- [ ] Tests unitaires"
story "Sprint 5" "$GH_RYAN" Must 3 regles "Règles R3, R4, R5" \
  "En tant que superviseur, je veux être alerté des variations brutales d'altitude, de vitesse ou de cap, afin de repérer un comportement anormal." \
  "- [ ] R3 > 15 m/s, R4 > 51 m/s en < 60 s, R5 > 45° en < 60 s\n- [ ] R5 gère le passage 350° → 10°\n- [ ] Tests unitaires"
story "Sprint 5" "$GH_RYAN" Must 3 regles "Enregistrer les alertes" \
  "En tant que superviseur, je veux que chaque alerte soit conservée avec son explication, afin de comprendre pourquoi elle a été levée." \
  "- [ ] Aéronef, règle, date, valeur observée, seuil, message\n- [ ] Pas de doublon pour une même situation"
story "Sprint 5" "$GH_LUCAS" Must 3 api "Rechercher un aéronef" \
  "En tant qu'utilisateur, je veux rechercher un aéronef par ICAO24 ou indicatif, afin de consulter ses données de vol." \
  "- [ ] Route GET /aircraft?q=\n- [ ] Route GET /aircraft/{icao24}\n- [ ] Tests d'intégration"
story "Sprint 5" "$GH_LUCAS" Must 2 api "Obtenir la trajectoire d'un aéronef" \
  "En tant qu'utilisateur, je veux récupérer les positions successives d'un aéronef, afin de tracer sa trajectoire." \
  "- [ ] Route GET /aircraft/{icao24}/trajectory\n- [ ] Positions triées par date"

# Sprint 6
story "Sprint 6" "$GH_TEDDY" Must 2 interface "Écran de connexion" \
  "En tant qu'utilisateur, je veux un écran de connexion simple, afin d'arriver directement sur mon écran selon mon profil." \
  "- [ ] Redirection recherche ou dashboard selon le rôle\n- [ ] Message clair en cas d'erreur"
story "Sprint 6" "$GH_TEDDY" Must 3 interface "Écran de recherche" \
  "En tant qu'utilisateur, je veux une barre de recherche, afin de trouver un aéronef en quelques secondes." \
  "- [ ] Liste de résultats avec identifiant, indicatif et statut"
story "Sprint 6" "$GH_TEDDY" Must 5 interface "Fiche aéronef avec carte" \
  "En tant qu'utilisateur, je veux voir la trajectoire sur une carte et l'évolution des paramètres, afin d'analyser le vol." \
  "- [ ] Carte Leaflet avec la trajectoire\n- [ ] Courbes altitude, vitesse, cap\n- [ ] Alertes de l'aéronef affichées"
story "Sprint 6" "$GH_TEDDY" Must 5 interface "Dashboard superviseur" \
  "En tant que superviseur, je veux une vue d'ensemble, afin de savoir ce qui ne va pas maintenant." \
  "- [ ] Nombre d'aéronefs suivis et d'alertes actives\n- [ ] Tableau des alertes\n- [ ] Carte globale"

# Sprint 7
story "Sprint 7" "$GH_RYAN" Should 3 regles "Configurer les règles" \
  "En tant que superviseur, je veux activer, désactiver et régler les seuils, afin d'ajuster la sensibilité sans redéployer." \
  "- [ ] Seuils stockés en base\n- [ ] Écran de configuration réservé au superviseur"
story "Sprint 7" "$GH_TEDDY" Should 3 interface "Filtrer et acquitter les alertes" \
  "En tant que superviseur, je veux filtrer et marquer une alerte comme traitée, afin de ne garder que ce qui reste à faire." \
  "- [ ] Filtres par règle, aéronef, date\n- [ ] Bouton d'acquittement"
story "Sprint 7" "$GH_TOV" Must 3 devops "Lancer toute l'application avec Docker Compose" \
  "En tant qu'équipe, nous voulons démarrer l'application en une commande, afin de faire la démo sur n'importe quel poste." \
  "- [ ] docker compose up lance base, collecteur, API et interface"
story "Sprint 7" "$GH_TOV" Should 2 devops "Documentation du code en ligne" \
  "En tant que développeur, je veux une documentation générée depuis les docstrings, afin de comprendre le code sans le lire." \
  "- [ ] Documentation générée (pdoc)\n- [ ] Publiée sur GitHub Pages"
story "Sprint 7" "$GH_LUCAS" Must 1 cadrage "Release v1.0 et rendu du 1er décembre" \
  "En tant que Product Owner, je veux livrer une version stable, afin de respecter l'échéance." \
  "- [ ] Tag v1.0.0 et release\n- [ ] Mail envoyé avec cahier des charges, lien et collaboratrice ajoutée"

# Sprint 8
story "Sprint 8" "" Must 3 soutenance "Présentation PowerPoint" \
  "En tant qu'équipe, nous voulons un support de 20 minutes, afin de présenter le projet, la méthode et les choix techniques." \
  "- [ ] Fichier .pptx\n- [ ] Captures du tableau Scrum, des PR et des releases"
story "Sprint 8" "$GH_TOV" Must 2 soutenance "Scénario de démo et répétitions" \
  "En tant qu'équipe, nous voulons une démo répétée, afin qu'elle tienne en 10 minutes sans accroc." \
  "- [ ] docs/demo.md minuté\n- [ ] Deux répétitions\n- [ ] Plan B avec les données de secours"
story "Sprint 8" "$GH_RYAN" Could 2 regles "Niveau de criticité des alertes" \
  "En tant que superviseur, je veux un niveau de criticité, afin de traiter d'abord les alertes graves." \
  "- [ ] Criticité par règle\n- [ ] Tri par criticité dans le dashboard"
story "Sprint 8" "$GH_LUCAS" Could 5 ia "Score d'anomalie par IA" \
  "En tant que superviseur, je veux un score d'anomalie appris sur l'historique, afin de le comparer aux règles fixes." \
  "- [ ] Isolation Forest entraîné sur les données collectées\n- [ ] Comparaison avec les alertes des règles"

# Fermer les milestones des sprints passés
for s in 0 1 2; do
  num=$(gh api "repos/$REPO/milestones?state=all" --jq ".[] | select(.title==\"Sprint $s\") | .number")
  gh api -X PATCH "repos/$REPO/milestones/$num" -f state=closed >/dev/null
done

echo "Backlog créé."
