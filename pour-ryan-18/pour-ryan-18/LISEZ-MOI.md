# Connexion (#18) rebranchée sur le reste du projet

Ce dossier reprend ton travail de la PR #58 (bcrypt, JWT, rôles, `ServiceAuthentification`, tes tests) et le branche sur la base et l'application communes. Tu le relis, tu le testes et tu le pousses toi-même sur ta branche `feat/18-auth`.

## Quand l'appliquer

Après la fusion dans `main` des PR #59 (base de données) et #60 (API). Le script vérifie ce point et s'arrête sinon.

## Comment l'appliquer

Depuis la racine du dépôt (sous Windows, dans Git Bash) :

```bash
bash chemin/vers/pour-ryan-18/appliquer.sh
```

Le script :

1. met ta branche à jour et y fusionne `main` ;
2. copie les fichiers du dossier `lot/` ;
3. supprime `backend/database.py`, `backend/dependencies.py` et `backend/models.py`, remplacés ;
4. lance `ruff check .` et `pytest` (53 tests attendus).

Il ne pousse rien. À la fin, il t'affiche les trois commandes pour committer et pousser, une fois que tu as relu.

## Ce qui change par rapport à ta PR

| Avant | Après |
|---|---|
| `backend/database.py` (psycopg2, `DATABASE_URL`, repli sur un fichier SQLite) | `BaseDeDonnees` de `backend/bdd.py`, la même connexion que la collecte et l'API |
| `backend/models.py` | Table `UtilisateurTable` dans `backend/bdd.py` (table `app_user`, comme dans le cahier des charges) |
| Routes en fonctions dans `backend/main.py` | Classe `ApiConnexion` dans `backend/api_connexion.py`, branchée dans `ApplicationAeroSafe` |
| `backend/dependencies.py` (`get_current_user`, `require_superviseur`) | Classe `GardeAcces` : même logique, 401 sans jeton valide, 403 si le rôle ne suffit pas |
| Aucun moyen de créer un compte | `python -m backend.creer_compte <email> [role]` |
| Routes `/aircraft` ouvertes | Toutes les routes sauf `/login` exigent un jeton (exigence BNF-03) |

Ce qui ne change pas : `ServiceAuthentification`, `schemas.py`, le format de `/login`, `/me` et `/superviseur`, et tes trois tests, complétés par douze autres (jeton expiré ou falsifié, compte en double, mot de passe jamais stocké en clair…).

Nouveautés à connaître :

- la classe `Utilisateur` du diagramme de classes (`verifier_mot_de_passe()`, `est_superviseur()`) ;
- une erreur claire si `JWT_SECRET` manque dans `.env` ;
- dans `/docs`, le bouton **Authorize** accepte directement le jeton.

## Pour tester à la main

```bash
docker compose up -d
python -m backend.creer_compte test@aerosafe.fr
python -m backend.creer_compte chef@aerosafe.fr superviseur
uvicorn backend.main:app --reload
```

Puis ouvre http://127.0.0.1:8000/docs, appelle `POST /login`, colle le jeton dans **Authorize** et essaie `/me`, `/superviseur` et `/aircraft`.

## Avant de demander la relecture

- Mets `Closes #18` dans la description de la PR #58.
- Mets à jour la partie « Comment vérifier » avec les commandes ci-dessus.

## Deux points à décider en équipe

- Le cahier des charges et les maquettes parlent d'un **identifiant** ; ton code utilise une **adresse e-mail**. Le lot garde l'e-mail. Il faudra aligner l'un sur l'autre.
- La page `frontend/login.html` contient encore des mots de passe en clair dans son JavaScript. Elle devra appeler `POST /login`.
