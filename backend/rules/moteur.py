"""
MoteurRegles — applique toutes les règles enregistrées sur un état de vol.
"""

from backend.rules.base import Regle
from collector.modeles import EtatVol


class MoteurRegles:
    """
    Orchestre l'évaluation de toutes les règles sur un état de vol donné.
    Les règles sont injectées à l'initialisation pour faciliter les tests et l'extension.
    """

    def __init__(self, regles: list[Regle]) -> None:
        self.regles = regles

    def evaluer(self, etat: EtatVol) -> list[str]:
        """
        Applique chaque règle sur l'état de vol.
        Retourne la liste des noms de règles déclenchées (liste vide = aucune anomalie).
        """
        declenchees = []
        for regle in self.regles:
            if regle.evaluer(etat):
                declenchees.append(regle.nom)
        return declenchees
