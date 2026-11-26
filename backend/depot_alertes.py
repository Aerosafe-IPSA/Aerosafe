"""Enregistrement et lecture des alertes dans la table ``alert``."""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, insert, select
from sqlalchemy.engine import Connection

from backend.bdd import AircraftTable, AlerteTable, BaseDeDonnees
from backend.rules.alerte import Alerte
from backend.schemas_alertes import AlerteVue, Statistiques


class DepotAlertes:
    """Enregistre les alertes du moteur de règles et les relit pour l'interface.

    Une anomalie qui dure serait signalée à chaque collecte : une alerte n'est
    donc pas enregistrée si la même règle a déjà signalé le même aéronef dans
    les dix minutes qui précèdent.
    """

    REGLES = ("R1", "R2", "R3", "R4", "R5")
    DELAI_DOUBLON = timedelta(minutes=10)

    def __init__(self, base: BaseDeDonnees) -> None:
        """Prépare le dépôt.

        Args:
            base: connexion à la base AeroSafe.
        """
        self._moteur = base.moteur

    def _existe(self, connexion: Connection, alerte: Alerte) -> bool:
        """Cherche une alerte récente de la même règle sur le même aéronef."""
        requete = select(AlerteTable.id).where(
            AlerteTable.icao24 == alerte.aeronef,
            AlerteTable.nom_regle == alerte.nom_regle,
            AlerteTable.date_heure > alerte.date_heure - self.DELAI_DOUBLON,
            AlerteTable.date_heure <= alerte.date_heure,
        )
        return connexion.execute(requete).first() is not None

    def existe_deja(self, alerte: Alerte) -> bool:
        """Indique si cette alerte ferait doublon avec une alerte déjà enregistrée.

        Args:
            alerte: l'alerte que le moteur de règles vient de produire.

        Returns:
            True si la même règle a signalé le même aéronef dans les dix minutes
            qui précèdent la date de l'alerte.
        """
        with self._moteur.connect() as connexion:
            return self._existe(connexion, alerte)

    def enregistrer(self, alertes: list[Alerte]) -> int:
        """Enregistre les alertes qui ne sont pas des doublons.

        Args:
            alertes: alertes produites par ``MoteurRegles.analyser()``.

        Returns:
            Le nombre d'alertes réellement enregistrées.
        """
        nouvelles = 0
        with self._moteur.begin() as connexion:
            for alerte in sorted(alertes, key=lambda a: a.date_heure):
                if self._existe(connexion, alerte):
                    continue
                connexion.execute(
                    insert(AlerteTable).values(
                        icao24=alerte.aeronef,
                        nom_regle=alerte.nom_regle,
                        date_heure=alerte.date_heure,
                        valeur_observee=alerte.valeur_observee,
                        seuil=alerte.seuil,
                        message=alerte.message,
                        statut=alerte.statut,
                    )
                )
                nouvelles += 1
        return nouvelles

    def lister(self, icao24: str | None = None, limite: int = 50) -> list[AlerteVue]:
        """Renvoie les alertes, de la plus récente à la plus ancienne.

        Args:
            icao24: pour ne garder que les alertes d'un aéronef (casse ignorée).
            limite: nombre maximal d'alertes.

        Returns:
            Les alertes, avec l'indicatif de l'aéronef concerné.
        """
        requete = (
            select(AlerteTable, AircraftTable.callsign)
            .outerjoin(AircraftTable, AircraftTable.icao24 == AlerteTable.icao24)
            .order_by(AlerteTable.date_heure.desc(), AlerteTable.id.desc())
            .limit(limite)
        )
        if icao24:
            requete = requete.where(AlerteTable.icao24 == icao24.strip().lower())
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete).all()
        return [
            AlerteVue(
                icao24=ligne.icao24,
                callsign=ligne.callsign,
                nom_regle=ligne.nom_regle,
                date_heure=ligne.date_heure,
                valeur_observee=ligne.valeur_observee,
                seuil=ligne.seuil,
                message=ligne.message,
                statut=ligne.statut,
            )
            for ligne in lignes
        ]

    def statistiques(self) -> Statistiques:
        """Compte les aéronefs suivis et les alertes, au total et par règle.

        Returns:
            Les chiffres du tableau de bord ; chaque règle R1 à R5 est présente,
            avec 0 si elle n'a déclenché aucune alerte.
        """
        par_regle = select(AlerteTable.nom_regle, func.count()).group_by(
            AlerteTable.nom_regle
        )
        with self._moteur.connect() as connexion:
            aeronefs = connexion.scalar(select(func.count()).select_from(AircraftTable))
            comptes = {nom: nombre for nom, nombre in connexion.execute(par_regle)}
        detail = {regle: comptes.get(regle, 0) for regle in self.REGLES}
        for regle, nombre in comptes.items():
            detail.setdefault(regle, nombre)
        return Statistiques(
            aeronefs_suivis=aeronefs or 0,
            alertes=sum(comptes.values()),
            alertes_par_regle=detail,
        )
