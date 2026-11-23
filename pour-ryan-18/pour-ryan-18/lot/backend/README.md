# Backend

API REST (FastAPI) et accès à la base PostgreSQL. Tout le code est organisé en classes.

| Fichier | Classe | Rôle |
|---|---|---|
| `bdd.py` | `BaseDeDonnees`, `AircraftTable`, `ObservationTable` | Connexion à la base et tables de l'historique |
| `depot_aeronefs.py` | `DepotAeronefs` | Lecture en base : recherche, fiche et trajet d'un aéronef |
| `schemas_aeronefs.py` | `ResumeAeronef`, `FicheAeronef`, `PositionTrajet` | Format des réponses de l'API |
| `api_aeronefs.py` | `ApiAeronefs` | Routes `/aircraft` |
| `security.py` | `ServiceAuthentification` | Hachage bcrypt des mots de passe et jetons JWT |
| `utilisateur.py` | `Utilisateur` | Compte et rôle (classe du diagramme de classes) |
| `depot_utilisateurs.py` | `DepotUtilisateurs` | Lecture et création des comptes (table `app_user`) |
| `schemas.py` | `LoginRequest`, `TokenResponse`, `UtilisateurInfo` | Format des échanges de connexion |
| `api_connexion.py` | `ApiConnexion`, `GardeAcces` | Routes `/login`, `/me`, `/superviseur` et contrôle d'accès |
| `creer_compte.py` | `CreateurCompte` | Création d'un compte en ligne de commande |
| `application.py` | `ApplicationAeroSafe` | Assemble l'application et branche les routes |
| `main.py` | — | Point d'entrée pour uvicorn |

## Lancer l'API

```bash
docker compose up -d
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

La documentation interactive est générée automatiquement : http://127.0.0.1:8000/docs

## Routes

| Route | Réponse |
|---|---|
| `GET /aircraft?q=afr&limite=50` | Aéronefs dont le code ICAO24 ou l'indicatif contient `q` (sans tenir compte de la casse), du plus récemment vu au plus ancien |
| `GET /aircraft/{icao24}` | Fiche d'un aéronef : identité, statut, dernière position, nombre de positions ; 404 s'il est inconnu |
| `GET /aircraft/{icao24}/trajectory?minutes=30` | Positions triées par date, sur les `minutes` qui précèdent la dernière position (tout l'historique par défaut) ; 404 s'il est inconnu |

Le statut vaut « Au sol », « Contact perdu » (aucun message depuis plus de 5 minutes, comme la règle R1) ou « En vol ». Les unités sont celles d'OpenSky (mètres, m/s, degrés) et les dates sont en UTC.

## Connexion et rôles

Toutes les routes, sauf `POST /login`, exigent un jeton (exigence BNF-03).

1. Ajouter `JWT_SECRET` dans `.env` (voir `.env.example`).
2. Créer un compte ; le mot de passe est demandé sans s'afficher :

```bash
python -m backend.creer_compte superviseur@aerosafe.fr superviseur
python -m backend.creer_compte utilisateur@aerosafe.fr
```

3. Se connecter : `POST /login` avec `{"email": "...", "mot_de_passe": "..."}` renvoie un `access_token`.
4. Envoyer ce jeton dans l'en-tête `Authorization: Bearer <jeton>` des autres requêtes. Dans `/docs`, le bouton **Authorize** le fait pour toutes les routes.

| Route | Accès | Réponse |
|---|---|---|
| `POST /login` | tout le monde | Jeton JWT ; 401 si l'adresse ou le mot de passe est faux, sans préciser lequel |
| `GET /me` | compte connecté | Adresse et rôle du compte |
| `GET /superviseur` | superviseur | 403 pour un simple utilisateur |
| `GET /aircraft…` | compte connecté | Voir plus haut ; 401 sans jeton |

Les mots de passe sont hachés avec bcrypt et ne sont jamais stockés ni renvoyés en clair.

## Ajouter des routes

Créer une classe d'API sur le modèle d'`ApiAeronefs`, puis ajouter son routeur dans `ApplicationAeroSafe._brancher_routes()`. Pour la protéger, passer `dependencies=[Depends(connexion.garde.verifier)]` (compte connecté) ou `connexion.garde_superviseur.verifier` (superviseur seulement).
