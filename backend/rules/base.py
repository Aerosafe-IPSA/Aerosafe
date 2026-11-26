"""
Classe abstraite Regle — interface commune à toutes les règles de détection d'anomalie.
"""

from abc import ABC, abstractmethod

from collector.modeles import EtatVol


class Regle(ABC):
    """
    Classe de base abstraite pour toutes les règles du moteur.
    Chaque règle concrète doit implémenter la méthode evaluer().
    """

    @abstractmethod
    def evaluer(self, etat: EtatVol) -> bool:
        """
        Evalue si l'état de vol déclenche cette règle.
        Retourne True si une anomalie est détectée, False sinon.
        """
        ...

    @property
    @abstractmethod
    def nom(self) -> str:
        """Nom court de la règle, utilisé dans les messages d'alerte."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Description humaine de l'anomalie détectée."""
        ...
