"""
R2 — Position GPS ancienne.
Déclenche une alerte si la dernière position GPS reçue date de plus de 10 minutes.
"""

from datetime import datetime, timedelta, timezone

from backend.rules.base import Regle
from collector.modeles import EtatVol

SEUIL = timedelta(minutes=10)


class R2PositionAncienne(Regle):
    """
    Règle R2 : la dernière position GPS connue date de plus de 10 minutes.
    Différent de R1 : on peut avoir un contact radio sans position GPS récente.
    """

    @property
    def nom(self) -> str:
        return "R2PositionAncienne"

    @property
    def description(self) -> str:
        return "Position GPS non mise à jour depuis plus de 10 minutes"

    def evaluer(self, etat: EtatVol) -> bool:
        """Retourne True si time_position est absent ou trop ancien."""
        if etat.time_position is None:
            return True  # Pas de position GPS = anomalie

        maintenant = datetime.now(timezone.utc)
        return (maintenant - etat.time_position) > SEUIL
