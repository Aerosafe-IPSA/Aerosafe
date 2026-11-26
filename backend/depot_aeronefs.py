"""Lecture en base des aéronefs et de leur historique de positions."""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy import and_, func, or_, select

from backend.bdd import AircraftTable, BaseDeDonnees, ObservationTable
from backend.schemas_aeronefs import FicheAeronef, PositionTrajet, ResumeAeronef


class DepotAeronefs:
    """Recherche les aéronefs et reconstruit leurs trajets à partir de la base.

    Le statut affiché suit le cahier des charges : « Au sol », « Contact perdu »
    (aucun message depuis plus de 5 minutes, comme la règle R1) ou « En vol ».
    """

    SEUIL_CONTACT_PERDU = timedelta(seconds=300)

    def __init__(self, base: BaseDeDonnees) -> None:
        """Prépare le dépôt.

        Args:
            base: connexion à la base AeroSafe.
        """
        self._moteur = base.moteur

    def _statut(self, observation) -> str:
        """Déduit le statut d'un aéronef de sa dernière observation."""
        if observation is None or observation.observed_at is None:
            return "Inconnu"
        if observation.on_ground:
            return "Au sol"
        if observation.last_contact is not None:
            silence = observation.observed_at - observation.last_contact
            if silence > self.SEUIL_CONTACT_PERDU:
                return "Contact perdu"
        return "En vol"

    @staticmethod
    def _position(observation) -> PositionTrajet:
        """Transforme une ligne de la table ``observation`` en position de trajet."""
        return PositionTrajet(
            horodatage=observation.observed_at,
            latitude=observation.latitude,
            longitude=observation.longitude,
            altitude=observation.baro_altitude,
            vitesse=observation.velocity,
            cap=observation.true_track,
            taux_vertical=observation.vertical_rate,
            au_sol=bool(observation.on_ground),
        )

    def rechercher(self, texte: str = "", limite: int = 50) -> list[ResumeAeronef]:
        """Cherche des aéronefs par code ICAO24 ou par indicatif.

        La recherche ignore la casse et accepte un morceau de code ou d'indicatif.
        Sans texte, les aéronefs vus le plus récemment sont renvoyés.

        Args:
            texte: début, milieu ou fin du code ICAO24 ou de l'indicatif.
            limite: nombre maximal de résultats.

        Returns:
            Les aéronefs trouvés, du plus récemment vu au plus ancien.
        """
        dernier_etat = and_(
            ObservationTable.icao24 == AircraftTable.icao24,
            ObservationTable.observed_at == AircraftTable.last_seen,
        )
        requete = (
            select(
                AircraftTable.icao24,
                AircraftTable.callsign,
                AircraftTable.origin_country,
                AircraftTable.last_seen,
                ObservationTable.observed_at,
                ObservationTable.on_ground,
                ObservationTable.last_contact,
                ObservationTable.baro_altitude,
                ObservationTable.latitude,
                ObservationTable.longitude,
            )
            .outerjoin(ObservationTable, dernier_etat)
            .order_by(AircraftTable.last_seen.desc(), AircraftTable.icao24)
            .limit(limite)
        )
        recherche = texte.strip().lower()
        if recherche:
            requete = requete.where(
                or_(
                    func.lower(AircraftTable.icao24).contains(
                        recherche, autoescape=True
                    ),
                    func.lower(AircraftTable.callsign).contains(
                        recherche, autoescape=True
                    ),
                )
            )
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete).all()
        return [
            ResumeAeronef(
                icao24=ligne.icao24,
                callsign=ligne.callsign,
                pays_origine=ligne.origin_country,
                statut=self._statut(ligne),
                latitude=ligne.latitude,
                longitude=ligne.longitude,
                altitude=ligne.baro_altitude,
                dernier_contact=ligne.last_contact,
                derniere_observation=ligne.last_seen,
            )
            for ligne in lignes
        ]

    def trouver(self, icao24: str) -> FicheAeronef | None:
        """Renvoie la fiche d'un aéronef.

        Args:
            icao24: adresse ICAO24, sans tenir compte de la casse.

        Returns:
            La fiche de l'aéronef, ou None s'il est inconnu.
        """
        code = icao24.strip().lower()
        with self._moteur.connect() as connexion:
            avion = connexion.execute(
                select(AircraftTable).where(AircraftTable.icao24 == code)
            ).first()
            if avion is None:
                return None
            derniere = connexion.execute(
                select(ObservationTable)
                .where(ObservationTable.icao24 == code)
                .order_by(ObservationTable.observed_at.desc())
                .limit(1)
            ).first()
            nombre = connexion.scalar(
                select(func.count())
                .select_from(ObservationTable)
                .where(ObservationTable.icao24 == code)
            )
        return FicheAeronef(
            icao24=avion.icao24,
            callsign=avion.callsign,
            pays_origine=avion.origin_country,
            statut=self._statut(derniere),
            premiere_observation=avion.first_seen,
            derniere_observation=avion.last_seen,
            dernier_contact=derniere.last_contact if derniere else None,
            nombre_positions=nombre,
            derniere_position=self._position(derniere) if derniere else None,
        )

    def trajet(
        self, icao24: str, minutes: int | None = None
    ) -> list[PositionTrajet] | None:
        """Renvoie les positions successives d'un aéronef, triées par date.

        Args:
            icao24: adresse ICAO24, sans tenir compte de la casse.
            minutes: durée à remonter depuis la dernière position connue ;
                None pour tout l'historique.

        Returns:
            Les positions de la plus ancienne à la plus récente, ou None si
            l'aéronef est inconnu.
        """
        code = icao24.strip().lower()
        with self._moteur.connect() as connexion:
            derniere = connexion.scalar(
                select(AircraftTable.last_seen).where(AircraftTable.icao24 == code)
            )
            if derniere is None:
                return None
            requete = (
                select(ObservationTable)
                .where(ObservationTable.icao24 == code)
                .order_by(ObservationTable.observed_at)
            )
            if minutes is not None:
                debut = derniere - timedelta(minutes=minutes)
                requete = requete.where(ObservationTable.observed_at >= debut)
            lignes = connexion.execute(requete).all()
        return [self._position(ligne) for ligne in lignes]
