"""Lecture en base des alertes et des chiffres du tableau de bord."""

from __future__ import annotations

from sqlalchemy import func, select

from backend.bdd import AircraftTable, AlerteTable, BaseDeDonnees
from backend.schemas_alertes import AlerteVue, Statistiques


class DepotAlertes:
    """Relit les alertes de la table ``alert`` pour l'interface."""

    REGLES = ("R1", "R2", "R3", "R4", "R5")

    def __init__(self, base: BaseDeDonnees) -> None:
        """Prépare le dépôt.

        Args:
            base: connexion à la base AeroSafe.
        """
        self._moteur = base.moteur

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
