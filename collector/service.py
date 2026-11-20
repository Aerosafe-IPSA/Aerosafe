"""Service qui enchaîne collecte OpenSky et enregistrement en base, en continu."""

from __future__ import annotations

import logging
import time

from sqlalchemy.exc import SQLAlchemyError

from collector.collecteur import CollecteurOpenSky, ErreurOpenSky
from collector.depot_positions import DepotPositions

logger = logging.getLogger("collector")


class ServiceCollecte:
    """Interroge OpenSky à intervalle régulier et enregistre chaque collecte.

    Une erreur d'OpenSky ou de la base est journalisée sans arrêter le service :
    la collecte reprend au cycle suivant (exigence BNF-02 du cahier des charges).
    """

    def __init__(
        self,
        collecteur: CollecteurOpenSky,
        depot: DepotPositions | None = None,
        intervalle_secondes: int = 60,
    ) -> None:
        """Prépare le service.

        Args:
            collecteur: le collecteur OpenSky à utiliser.
            depot: où enregistrer les positions ; None pour ne rien enregistrer.
            intervalle_secondes: délai entre le début de deux collectes.
        """
        self._collecteur = collecteur
        self._depot = depot
        self._intervalle = intervalle_secondes

    @property
    def intervalle(self) -> int:
        """Délai entre deux collectes, en secondes."""
        return self._intervalle

    def executer_cycle(self) -> int:
        """Fait une collecte puis l'enregistre en base.

        Returns:
            Le nombre de nouvelles positions enregistrées (0 en cas d'erreur).
        """
        try:
            aeronefs = self._collecteur.recuperer_etats()
            logger.info("Collecte terminée : %d aéronefs", len(aeronefs))
            if self._depot is None:
                return 0
            nouvelles = self._depot.enregistrer(aeronefs)
            logger.info("%d nouvelles positions enregistrées en base", nouvelles)
            return nouvelles
        except ErreurOpenSky as erreur:
            logger.warning("Collecte ignorée : %s", erreur)
        except SQLAlchemyError as erreur:
            logger.error("Enregistrement en base impossible : %s", erreur)
        return 0

    def lancer(self, cycles: int | None = None) -> None:
        """Enchaîne les cycles de collecte.

        Args:
            cycles: nombre de cycles à faire ; None pour tourner sans fin.
        """
        fait = 0
        while cycles is None or fait < cycles:
            debut = time.monotonic()
            self.executer_cycle()
            fait += 1
            if cycles is None or fait < cycles:
                time.sleep(max(0.0, self._intervalle - (time.monotonic() - debut)))
