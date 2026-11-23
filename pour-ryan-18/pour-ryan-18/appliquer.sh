#!/bin/bash
# Rebranche la connexion (#18) sur BaseDeDonnees et ApplicationAeroSafe.
# À lancer depuis la racine du dépôt :  bash chemin/vers/pour-ryan-18/appliquer.sh
# Le script prépare tout et lance les tests, mais ne committe et ne pousse rien.
set -euo pipefail

LOT="$(cd "$(dirname "$0")" && pwd)"
BRANCHE="feat/18-auth"

arreter() {
  echo ""
  echo "ARRÊT : $1"
  exit 1
}

somme() {
  if command -v md5sum >/dev/null 2>&1; then md5sum "$1" | cut -d' ' -f1; else md5 -q "$1"; fi
}

[ -d .git ] || arreter "lance ce script depuis la racine du dépôt AeroSafe"
[ -z "$(git status --porcelain)" ] || arreter "des fichiers sont modifiés (voir git status). Committe-les ou range-les d'abord."

echo "== 1/5  Mise à jour de la branche $BRANCHE"
git checkout -q "$BRANCHE"
git pull -q --ff-only || arreter "impossible de mettre $BRANCHE à jour"
git fetch -q origin main

echo "== 2/5  Vérification que main contient l'API"
git cat-file -e origin/main:backend/application.py 2>/dev/null \
  || arreter "la PR de l'API (#23 et #24) n'est pas encore fusionnée dans main. Réessaie après sa fusion."
while read -r attendu fichier; do
  [ -n "$fichier" ] || continue
  actuel="$(git show "origin/main:$fichier" | { if command -v md5sum >/dev/null 2>&1; then md5sum | cut -d' ' -f1; else md5 -q; fi; })"
  [ "$actuel" = "$attendu" ] || arreter "$fichier a changé sur main depuis la préparation de ce lot : demande un lot à jour à Lucas."
done < "$LOT/bases.txt"

echo "== 3/5  Fusion de main dans $BRANCHE"
git merge -q -X theirs origin/main -m "Merge branch 'main' into $BRANCHE" \
  || arreter "la fusion de main a échoué : annule avec  git merge --abort  et préviens Lucas."

echo "== 4/5  Copie des fichiers rebranchés"
git checkout -q origin/main -- .
cp -R "$LOT/lot/." .
for ancien in backend/database.py backend/dependencies.py backend/models.py; do
  if [ -f "$ancien" ]; then git rm -q -f "$ancien"; fi
done
rm -f aerosafe_test.db

echo "== 5/5  Installation des dépendances, ruff et pytest"
PYTHON="python"
if [ -x .venv/bin/python ]; then PYTHON=".venv/bin/python"; fi
if [ -x .venv/Scripts/python.exe ]; then PYTHON=".venv/Scripts/python.exe"; fi
"$PYTHON" -m pip install -q -r requirements.txt pytest ruff
"$PYTHON" -m ruff check . || arreter "ruff signale des erreurs"
"$PYTHON" -m pytest -q || arreter "des tests échouent"

echo ""
echo "PRÊT : 53 tests attendus. La fusion de main est enregistrée sur ton poste, le reste est en attente, et rien n'est poussé."
echo "Relis les changements avec  git status  et  git diff --cached"
echo "Puis, quand tu es d'accord :"
echo "  git add -A"
echo "  git commit -m \"refactor(#18): branche la connexion sur BaseDeDonnees et ApplicationAeroSafe\""
echo "  git push"
