"""Détection des anomalies dans l'historique déjà enregistré.

Utile après avoir chargé les données de secours, ou pour appliquer les règles
à des positions collectées avant leur mise en place :

    python -m collector.rejeu
"""

from __future__ import annotations

from dotenv import load_dotenv
from sqlalchemy import select

from backend.bdd import BaseDeDonnees, BaseInjoignableError, ObservationTable
from backend.depot_alertes import DepotAlertes
from backend.rules.moteur import MoteurRegles
from collector.modeles import Aeronef, EtatVol


class RejeuHistorique:
    """Rejoue les observations de la base dans le moteur de règles.

    Chaque aéronef retrouve ses états dans l'ordre où ils ont été reçus, comme
    pendant la collecte. Les alertes déjà enregistrées ne sont pas dupliquées :
    le rejeu peut être lancé plusieurs fois.
    """

    def __init__(
        self, base: BaseDeDonnees, moteur: MoteurRegles, depot_alertes: DepotAlertes
    ) -> None:
        """Prépare le rejeu.

        Args:
            base: connexion à la base AeroSafe.
            moteur: règles à appliquer.
            depot_alertes: où enregistrer les alertes.
        """
        self._moteur_base = base.moteur
        self._regles = moteur
        self._depot_alertes = depot_alertes

    @staticmethod
    def _etat(ligne) -> EtatVol:
        """Transforme une ligne de la table ``observation`` en état de vol."""
        return EtatVol(
            horodatage=ligne.observed_at,
            latitude=ligne.latitude,
            longitude=ligne.longitude,
            altitude=ligne.baro_altitude,
            vitesse=ligne.velocity,
            cap=ligne.true_track,
            taux_vertical=ligne.vertical_rate,
            au_sol=bool(ligne.on_ground),
            last_contact=ligne.last_contact,
            time_position=ligne.time_position,
        )

    def rejouer(self) -> int:
        """Applique les règles à tout l'historique et enregistre les alertes.

        Returns:
            Le nombre de nouvelles alertes enregistrées.
        """
        requete = select(ObservationTable).order_by(
            ObservationTable.icao24, ObservationTable.observed_at
        )
        alertes = []
        aeronef = None
        with self._moteur_base.connect() as connexion:
            for ligne in connexion.execute(requete):
                if aeronef is None or aeronef.icao24 != ligne.icao24:
                    aeronef = Aeronef(ligne.icao24, None, None)
                aeronef.ajouter_etat(self._etat(ligne))
                alertes.extend(self._regles.analyser(aeronef))
        return self._depot_alertes.enregistrer(alertes)


def main() -> None:
    """Point d'entrée : ``python -m collector.rejeu``."""
    load_dotenv()
    try:
        base = BaseDeDonnees()
    except BaseInjoignableError as erreur:
        print(f"Erreur : {erreur}")
        raise SystemExit(1) from erreur
    rejeu = RejeuHistorique(base, MoteurRegles(), DepotAlertes(base))
    print(f"{rejeu.rejouer()} nouvelles alertes enregistrées")


if __name__ == "__main__":
    main()
