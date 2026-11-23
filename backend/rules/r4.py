"""R4 — Variation brutale de vitesse (seuil : 51 m/s)."""

from __future__ import annotations

from backend.rules.alerte import Alerte
from backend.rules.base import Regle
from collector.modeles import Aeronef

INTERVALLE_MAX = 90.0


class R4VariationVitesse(Regle):
    """Règle R4 : écart de vitesse entre les deux dernières observations dépasse 51 m/s."""

    def __init__(self, seuil: float = 51.0) -> None:
        """Crée la règle avec son seuil en m/s."""
        super().__init__("R4", seuil)

    def evaluer(self, aeronef: Aeronef) -> Alerte | None:
        """Renvoie une alerte si la variation de vitesse dépasse le seuil."""
        etat = aeronef.derniere_position()
        precedent = aeronef.etat_precedent()

        if etat is None or precedent is None:
            return None
        if etat.vitesse is None or precedent.vitesse is None:
            return None

        # Ignore les comparaisons avec un trop grand écart temporel (collecte manquée)
        intervalle = (etat.horodatage - precedent.horodatage).total_seconds()
        if not (0 < intervalle <= INTERVALLE_MAX):
            return None

        valeur = abs(etat.vitesse - precedent.vitesse)
        if valeur <= self._seuil:
            return None
        message = f"Variation de vitesse de {valeur:.1f} m/s (seuil : {self._seuil:.0f} m/s)"
        return self._alerte(aeronef, etat, valeur, message)
