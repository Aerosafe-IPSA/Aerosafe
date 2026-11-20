"""Lance la collecte OpenSky toutes les 60 secondes : ``python -m collector``."""

from __future__ import annotations

import logging
import time

from dotenv import load_dotenv

from collector.collecteur import CollecteurOpenSky, ErreurOpenSky

INTERVALLE_SECONDES = 60
logger = logging.getLogger("collector")


def boucle(collecteur: CollecteurOpenSky, cycles: int | None = None) -> None:
    """Interroge OpenSky à intervalle régulier sans jamais s'arrêter sur une erreur.

    Args:
        collecteur: le collecteur à utiliser.
        cycles: nombre de collectes à faire ; None pour tourner sans fin.
    """
    fait = 0
    while cycles is None or fait < cycles:
        debut = time.monotonic()
        try:
            aeronefs = collecteur.recuperer_etats()
            logger.info("Collecte terminée : %d aéronefs", len(aeronefs))
        except ErreurOpenSky as erreur:
            logger.warning("Collecte ignorée : %s", erreur)
        fait += 1
        if cycles is None or fait < cycles:
            time.sleep(max(0.0, INTERVALLE_SECONDES - (time.monotonic() - debut)))


def main() -> None:
    """Point d'entrée : lit le fichier .env et lance la boucle de collecte."""
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    collecteur = CollecteurOpenSky()
    mode = "OAuth2" if collecteur.authentifie else "anonyme"
    logger.info("Collecte OpenSky toutes les %d s (mode %s)", INTERVALLE_SECONDES, mode)
    boucle(collecteur)


if __name__ == "__main__":
    main()
