"""MoteurRegles — applique toutes les règles sur un aéronef et collecte les alertes."""

from __future__ import annotations

from backend.rules.alerte import Alerte
from backend.rules.base import Regle
from backend.rules.r1 import R1DelaiContact
from backend.rules.r2 import R2PositionAncienne
from backend.rules.r3 import R3VariationAltitude
from backend.rules.r4 import R4VariationVitesse
from backend.rules.r5 import R5ChangementCap
from collector.modeles import Aeronef


class MoteurRegles:
    """Orchestre l'évaluation de toutes les règles sur un aéronef."""

    def __init__(self, regles: list[Regle] | None = None) -> None:
        """Crée le moteur avec les règles données, ou les cinq règles par défaut."""
        self.regles = regles if regles is not None else self.regles_par_defaut()

    def analyser(self, aeronef: Aeronef) -> list[Alerte]:
        """Applique chaque règle et renvoie la liste des alertes déclenchées."""
        alertes = []
        for regle in self.regles:
            alerte = regle.evaluer(aeronef)
            if alerte is not None:
                alertes.append(alerte)
        return alertes

    @staticmethod
    def regles_par_defaut() -> list[Regle]:
        """Renvoie les cinq règles avec leurs seuils du cahier des charges."""
        return [
            R1DelaiContact(),
            R2PositionAncienne(),
            R3VariationAltitude(),
            R4VariationVitesse(),
            R5ChangementCap(),
        ]
