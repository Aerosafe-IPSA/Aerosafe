# Collecteur

Service qui interroge l'API OpenSky toutes les 60 secondes sur la France métropolitaine.

- `modeles.py` : classes `Aeronef` et `EtatVol` (voir `docs/conception/classes.md`)
- `collecteur.py` : classe `CollecteurOpenSky` (OAuth2, quota dépassé, valeurs manquantes)
- `depot_positions.py` : classe `DepotPositions`, qui enregistre chaque position en base sans doublon
- `service.py` : classe `ServiceCollecte`, qui enchaîne collecte, enregistrement et détection des anomalies
- `rejeu.py` : classe `RejeuHistorique`, qui applique les règles à l'historique déjà en base
- `__main__.py` : assemble les objets et lance le service

## Lancer la collecte

```bash
docker compose up -d
pip install -r requirements.txt
python -m collector
```

La base PostgreSQL doit tourner (`docker compose up -d`, voir le README principal). Les tables `aircraft` et `observation` sont créées automatiquement au premier lancement (modèle de données du cahier des charges V3, chapitre Conception).

Avec `OPENSKY_CLIENT_ID` et `OPENSKY_CLIENT_SECRET` dans `.env`, l'accès se fait en OAuth2 ; sinon en mode anonyme, au quota plus faible. Une erreur d'OpenSky (quota dépassé, API injoignable) ou de la base est journalisée, et la collecte reprend au cycle suivant.

## Détection des anomalies

À chaque collecte, `ServiceCollecte` applique les règles R1 à R5 (`backend/rules/`) à chaque aéronef et enregistre les alertes dans la table `alert` (`backend/depot_alertes.py`). Le journal l'indique : « N nouvelles alertes enregistrées ».

- Les règles R4 et R5 comparent deux observations : le service garde donc en mémoire les aéronefs suivis d'une collecte à l'autre.
- Une anomalie qui dure n'est enregistrée qu'une fois : la même règle ne signale pas le même aéronef deux fois en dix minutes.

Pour appliquer les règles à des positions déjà en base (par exemple après `python -m collector.donnees_demo charger`) :

```bash
python -m collector.rejeu
```
