"""Création d'un compte en ligne de commande.

Exemple : ``python -m backend.creer_compte superviseur@aerosafe.fr superviseur``
Le mot de passe est demandé ensuite, sans s'afficher à l'écran.
"""

from __future__ import annotations

import argparse
import getpass
import sys

from dotenv import load_dotenv

from backend.bdd import BaseDeDonnees, BaseInjoignableError
from backend.depot_utilisateurs import CompteExistantError, DepotUtilisateurs
from backend.utilisateur import Utilisateur


class CreateurCompte:
    """Lit les arguments de la commande et crée le compte demandé."""

    def __init__(self, depot: DepotUtilisateurs) -> None:
        """Prépare la commande.

        Args:
            depot: le dépôt où enregistrer le compte.
        """
        self._depot = depot

    def executer(self, arguments: list[str], mot_de_passe: str | None = None) -> str:
        """Crée le compte décrit par les arguments.

        Args:
            arguments: adresse puis rôle (facultatif, « utilisateur » par défaut).
            mot_de_passe: mot de passe ; demandé au clavier s'il est absent.

        Returns:
            Le message de confirmation.

        Raises:
            CompteExistantError: un compte utilise déjà cette adresse.
        """
        analyseur = argparse.ArgumentParser(description="Crée un compte AeroSafe.")
        analyseur.add_argument("email")
        analyseur.add_argument(
            "role",
            nargs="?",
            default=Utilisateur.ROLE_UTILISATEUR,
            choices=Utilisateur.ROLES,
        )
        choix = analyseur.parse_args(arguments)
        if mot_de_passe is None:
            mot_de_passe = getpass.getpass("Mot de passe : ")
        compte = self._depot.creer(choix.email, mot_de_passe, choix.role)
        return f"Compte créé : {compte.email} ({compte.role})"


def main() -> None:
    """Point d'entrée : ``python -m backend.creer_compte <email> [role]``."""
    load_dotenv()
    try:
        createur = CreateurCompte(DepotUtilisateurs(BaseDeDonnees()))
        print(createur.executer(sys.argv[1:]))
    except (BaseInjoignableError, CompteExistantError) as erreur:
        print(f"Erreur : {erreur}")
        sys.exit(1)


if __name__ == "__main__":
    main()
