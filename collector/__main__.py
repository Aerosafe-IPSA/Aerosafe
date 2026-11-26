"""Point d'entrée de la collecte : ``python -m collector``."""

from __future__ import annotations

import logging
import sys

from dotenv import load_dotenv

from backend.bdd import BaseDeDonnees, BaseInjoignableError
from backend.depot_alertes import DepotAlertes
from backend.rules.moteur import MoteurRegles
from collector.collecteur import CollecteurOpenSky
from collector.depot_positions import DepotPositions
from collector.service import ServiceCollecte


def main() -> None:
    """Lit le fichier .env, assemble les objets et lance le service de collecte.

    Si la base ne répond pas, un message clair est affiché et le programme s'arrête.
    """
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    journal = logging.getLogger("collector")
    collecteur = CollecteurOpenSky()
    try:
        base = BaseDeDonnees()
    except BaseInjoignableError as erreur:
        journal.error("%s", erreur)
        sys.exit(1)
    service = ServiceCollecte(
        collecteur,
        DepotPositions(base),
        moteur=MoteurRegles(),
        depot_alertes=DepotAlertes(base),
    )
    mode = "OAuth2" if collecteur.authentifie else "anonyme"
    journal.info("Collecte OpenSky toutes les %d s (mode %s)", service.intervalle, mode)
    service.lancer()


if __name__ == "__main__":
    main()
