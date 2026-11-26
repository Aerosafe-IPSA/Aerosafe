"""Service qui enchaîne collecte OpenSky, enregistrement en base et détection."""

from __future__ import annotations

import logging
import time

from sqlalchemy.exc import SQLAlchemyError

from backend.depot_alertes import DepotAlertes
from backend.rules.moteur import MoteurRegles
from collector.collecteur import CollecteurOpenSky, ErreurOpenSky
from collector.depot_positions import DepotPositions
from collector.modeles import Aeronef

logger = logging.getLogger("collector")


class ServiceCollecte:
    """Interroge OpenSky à intervalle régulier et enregistre chaque collecte.

    Avec un moteur de règles et un dépôt d'alertes, chaque collecte est aussi
    analysée : les anomalies détectées sont enregistrées dans la table ``alert``.

    Une erreur d'OpenSky ou de la base est journalisée sans arrêter le service :
    la collecte reprend au cycle suivant (exigence BNF-02 du cahier des charges).
    """

    def __init__(
        self,
        collecteur: CollecteurOpenSky,
        depot: DepotPositions | None = None,
        intervalle_secondes: int = 60,
        moteur: MoteurRegles | None = None,
        depot_alertes: DepotAlertes | None = None,
    ) -> None:
        """Prépare le service.

        Args:
            collecteur: le collecteur OpenSky à utiliser.
            depot: où enregistrer les positions ; None pour ne rien enregistrer.
            intervalle_secondes: délai entre le début de deux collectes.
            moteur: règles à appliquer à chaque collecte ; None pour ne rien détecter.
            depot_alertes: où enregistrer les alertes ; None pour ne rien détecter.
        """
        self._collecteur = collecteur
        self._depot = depot
        self._intervalle = intervalle_secondes
        self._regles = moteur
        self._depot_alertes = depot_alertes
        # Aéronefs suivis d'une collecte à l'autre, par code ICAO24
        self._suivis: dict[str, Aeronef] = {}

    @property
    def intervalle(self) -> int:
        """Délai entre deux collectes, en secondes."""
        return self._intervalle

    def executer_cycle(self) -> int:
        """Fait une collecte, l'enregistre en base puis y cherche des anomalies.

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
            self._detecter(aeronefs)
            return nouvelles
        except ErreurOpenSky as erreur:
            logger.warning("Collecte ignorée : %s", erreur)
        except SQLAlchemyError as erreur:
            logger.error("Enregistrement en base impossible : %s", erreur)
        return 0

    def _suivre(self, aeronefs: list[Aeronef]) -> list[Aeronef]:
        """Ajoute chaque état reçu à l'historique gardé en mémoire.

        Le collecteur renvoie à chaque cycle des aéronefs neufs, avec un seul
        état. Les règles R4 et R5 comparent deux observations : il faut donc
        retrouver l'aéronef déjà suivi et lui ajouter son nouvel état.

        Args:
            aeronefs: aéronefs renvoyés par la collecte du cycle.

        Returns:
            Les mêmes aéronefs, tels qu'ils sont suivis, avec leur historique.
        """
        suivis = []
        for recu in aeronefs:
            etat = recu.derniere_position()
            if etat is None:
                continue
            connu = self._suivis.get(recu.icao24)
            if connu is None:
                self._suivis[recu.icao24] = connu = recu
            else:
                connu.ajouter_etat(etat)
            suivis.append(connu)
        return suivis

    def _detecter(self, aeronefs: list[Aeronef]) -> int:
        """Applique les règles aux aéronefs de la collecte et enregistre les alertes.

        Returns:
            Le nombre de nouvelles alertes enregistrées.
        """
        if self._regles is None or self._depot_alertes is None:
            return 0
        alertes = []
        for aeronef in self._suivre(aeronefs):
            alertes.extend(self._regles.analyser(aeronef))
        nouvelles = self._depot_alertes.enregistrer(alertes)
        logger.info("%d nouvelles alertes enregistrées", nouvelles)
        return nouvelles

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
