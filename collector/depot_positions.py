"""Enregistrement en base des positions récupérées par le collecteur."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.dialects import postgresql, sqlite

from backend.bdd import AircraftTable, BaseDeDonnees, ObservationTable
from collector.modeles import Aeronef


class DepotPositions:
    """Enregistre l'historique des positions dans les tables ``aircraft`` et ``observation``.

    Une observation déjà présente (même aéronef, même instant) est ignorée :
    on peut donc enregistrer deux fois la même collecte sans créer de doublon.
    """

    def __init__(self, base: BaseDeDonnees) -> None:
        """Prépare le dépôt.

        Args:
            base: connexion à la base (PostgreSQL, ou SQLite pour les tests).
        """
        self._moteur = base.moteur
        dialecte = self._moteur.dialect.name
        self._insert = postgresql.insert if dialecte == "postgresql" else sqlite.insert

    def enregistrer(self, aeronefs: list[Aeronef]) -> int:
        """Enregistre la dernière position de chaque aéronef.

        Les aéronefs inconnus sont créés, les autres voient leur indicatif et leur
        date de dernière apparition mis à jour.

        Args:
            aeronefs: aéronefs renvoyés par ``CollecteurOpenSky.recuperer_etats()``.

        Returns:
            Le nombre de nouvelles observations réellement enregistrées.
        """
        lignes_avions: dict[str, dict] = {}
        lignes_observations: dict[tuple, dict] = {}
        for aeronef in aeronefs:
            etat = aeronef.derniere_position()
            if etat is None or etat.horodatage is None:
                continue
            lignes_avions[aeronef.icao24] = {
                "icao24": aeronef.icao24,
                "callsign": aeronef.callsign,
                "origin_country": aeronef.pays_origine,
                "first_seen": etat.horodatage,
                "last_seen": etat.horodatage,
            }
            lignes_observations[(aeronef.icao24, etat.horodatage)] = {
                "icao24": aeronef.icao24,
                "observed_at": etat.horodatage,
                "latitude": etat.latitude,
                "longitude": etat.longitude,
                "baro_altitude": etat.altitude,
                "velocity": etat.vitesse,
                "true_track": etat.cap,
                "vertical_rate": etat.taux_vertical,
                "on_ground": etat.au_sol,
                "last_contact": etat.last_contact,
                "time_position": etat.time_position,
            }
        if not lignes_observations:
            return 0

        requete_avions = self._insert(AircraftTable).values(
            list(lignes_avions.values())
        )
        requete_avions = requete_avions.on_conflict_do_update(
            index_elements=["icao24"],
            set_={
                "callsign": requete_avions.excluded.callsign,
                "last_seen": requete_avions.excluded.last_seen,
            },
        )
        requete_observations = (
            self._insert(ObservationTable)
            .values(list(lignes_observations.values()))
            .on_conflict_do_nothing(index_elements=["icao24", "observed_at"])
            .returning(ObservationTable.id)
        )
        with self._moteur.begin() as connexion:
            connexion.execute(requete_avions)
            return len(connexion.execute(requete_observations).all())

    def nombre_observations(self, icao24: str) -> int:
        """Compte les observations enregistrées pour un aéronef.

        Args:
            icao24: adresse ICAO24 de l'aéronef.

        Returns:
            Le nombre de positions conservées pour cet aéronef.
        """
        requete = (
            select(func.count())
            .select_from(ObservationTable)
            .where(ObservationTable.icao24 == icao24)
        )
        with self._moteur.connect() as connexion:
            return connexion.scalar(requete)
