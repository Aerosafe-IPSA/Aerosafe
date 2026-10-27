#!/usr/bin/env bash
# Corrige les auteurs et les sprints des premières versions du cahier des charges :
#   V1 = Teddy (14 sept.), V2 = Ryan + Lucas (15 sept., avec le diagramme de cas d'utilisation).
# Ajoute aussi l'issue « Étudier l'API OpenSky » (sprint 1), oubliée dans le backlog.
# À lancer une seule fois, APRÈS scripts/simplifier_issues.sh.
set -euo pipefail
REPO="aerosafe-ipsa/aerosafe"
LUCAS="lleuginer"; RYAN="Zilwaa974"; TEDDY="teddymbatna-sketch"

ms() { gh api "repos/$REPO/milestones?state=all" --jq ".[] | select(.title==\"$1\") | .number"; }
S0=$(ms "Sprint 0"); S1=$(ms "Sprint 1")
set_ms() { gh api -X PATCH "repos/$REPO/issues/$1" -F milestone="$2" >/dev/null; }

# #2 V1 : Teddy
gh issue edit 2 --repo "$REPO" --remove-assignee "$RYAN" --add-assignee "$TEDDY" >/dev/null
echo "#2 V1 → Teddy"
# #3 V2 : Ryan + Lucas, sprint 0, 5 points
gh issue edit 3 --repo "$REPO" --remove-assignee "$TEDDY" --add-assignee "$RYAN,$LUCAS" \
  --remove-label "points:3" --add-label "points:5" >/dev/null
set_ms 3 "$S0"; echo "#3 V2 → Ryan + Lucas, sprint 0"
# #4 seuils des règles : Ryan + Lucas, sprint 0, 2 points
gh issue edit 4 --repo "$REPO" --add-assignee "$RYAN" --remove-label "points:5" --add-label "points:2" >/dev/null
set_ms 4 "$S0"; echo "#4 seuils → Ryan + Lucas, sprint 0"
# #5 diagramme de cas d'utilisation : Ryan + Lucas, sprint 0
gh issue edit 5 --repo "$REPO" --add-assignee "$RYAN" >/dev/null
set_ms 5 "$S0"; echo "#5 diagramme → Ryan + Lucas, sprint 0"

# Nouvelle issue : étude de l'API OpenSky (sprint 1, déjà faite)
body=$(printf '**Objectif**\n\nNous souhaitons comprendre ce que l'"'"'API OpenSky permet de récupérer et ses limites, avant de coder la collecte.\n\n**Critères de validation**\n\n- [x] Authentification OAuth2 et quotas de crédits identifiés\n- [x] Champ utile à chaque règle R1 à R5 identifié\n- [x] Besoin de stocker tout l'"'"'historique des positions identifié\n\n**Priorité** : Must · 2 point(s)\n')
url=$(gh issue create --repo "$REPO" --title "Étudier l'API OpenSky" --body "$body" \
  --label "user-story,must,points:2,epic:donnees,a-posteriori" --assignee "$LUCAS")
num=${url##*/}
set_ms "$num" "$S1"
gh issue close "$num" --repo "$REPO" --comment "Réalisé pendant le Sprint 1, avant la mise en place du suivi GitHub. Voir docs/scrum/sprints/." >/dev/null
echo "#$num Étudier l'API OpenSky → Lucas, sprint 1, fermée"
echo "Corrections terminées."
