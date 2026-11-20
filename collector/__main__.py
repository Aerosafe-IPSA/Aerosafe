"""Point d'entrée de la collecte : ``python -m collector``."""

from __future__ import annotations

import logging

from dotenv import load_dotenv

from backend.bdd import BaseDeDonnees
from collector.collecteur import CollecteurOpenSky
from collector.depot_positions import DepotPositions
from collector.service import ServiceCollecte


def main() -> None:
    """Lit le fichier .env, assemble les objets et lance le service de collecte."""
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    collecteur = CollecteurOpenSky()
    service = ServiceCollecte(collecteur, DepotPositions(BaseDeDonnees()))
    mode = "OAuth2" if collecteur.authentifie else "anonyme"
    logging.getLogger("collector").info(
        "Collecte OpenSky toutes les %d s (mode %s)", service.intervalle, mode
    )
    service.lancer()


if __name__ == "__main__":
    main()
