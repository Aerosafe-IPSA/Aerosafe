# Collecteur

Service qui interroge l'API OpenSky toutes les 60 secondes sur la France métropolitaine.

- `modeles.py` : classes `Aeronef` et `EtatVol` (voir `docs/conception/classes.md`)
- `collecteur.py` : classe `CollecteurOpenSky` (OAuth2, quota dépassé, valeurs manquantes)
- `depot_positions.py` : classe `DepotPositions`, qui enregistre chaque position en base sans doublon
- `__main__.py` : boucle de collecte et d'enregistrement

## Lancer la collecte

```bash
docker compose up -d
pip install -r requirements.txt
python -m collector
```

La base PostgreSQL doit tourner (`docker compose up -d`, voir le README principal). Les tables `aircraft` et `observation` sont créées automatiquement au premier lancement (modèle de données du cahier des charges V3, chapitre Conception).

Avec `OPENSKY_CLIENT_ID` et `OPENSKY_CLIENT_SECRET` dans `.env`, l'accès se fait en OAuth2 ; sinon en mode anonyme, au quota plus faible. Une erreur d'OpenSky (quota dépassé, API injoignable) ou de la base est journalisée, et la collecte reprend au cycle suivant.
