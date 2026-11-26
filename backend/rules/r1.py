"""
R1 — Délai de contact dépassé.
Déclenche une alerte si l'avion n'a pas été contacté depuis plus de 5 minutes.
"""

from datetime import datetime, timedelta, timezone

from backend.rules.base import Regle
from collector.modeles import EtatVol

SEUIL = timedelta(minutes=5)


class R1DelaiContact(Regle):
    """
    Règle R1 : le dernier contact radio date de plus de 5 minutes.
    Peut indiquer une perte de signal ou une panne du transpondeur.
    """

    @property
    def nom(self) -> str:
        return "R1DelaiContact"

    @property
    def description(self) -> str:
        return "Aucun contact depuis plus de 5 minutes"

    def evaluer(self, etat: EtatVol) -> bool:
        """Retourne True si last_contact est absent ou trop ancien."""
        if etat.last_contact is None:
            return True  # Pas de donnée de contact = anomalie par défaut

        maintenant = datetime.now(timezone.utc)
        return (maintenant - etat.last_contact) > SEUIL
