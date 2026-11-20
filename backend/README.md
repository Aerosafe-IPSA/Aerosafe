# Backend

API REST (FastAPI) et accès à la base PostgreSQL. Tout le code est organisé en classes.

| Fichier | Classe | Rôle |
|---|---|---|
| `bdd.py` | `BaseDeDonnees`, `AircraftTable`, `ObservationTable` | Connexion à la base et tables de l'historique |
| `depot_aeronefs.py` | `DepotAeronefs` | Lecture en base : recherche, fiche et trajet d'un aéronef |
| `schemas_aeronefs.py` | `ResumeAeronef`, `FicheAeronef`, `PositionTrajet` | Format des réponses de l'API |
| `api_aeronefs.py` | `ApiAeronefs` | Routes `/aircraft` |
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

## Ajouter des routes

Créer une classe d'API sur le modèle d'`ApiAeronefs`, puis ajouter son routeur dans `ApplicationAeroSafe._brancher_routes()`. Les routes de connexion (#18) protégeront ensuite l'ensemble de l'API par jeton.
