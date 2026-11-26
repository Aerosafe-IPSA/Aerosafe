"""Classe métier ``Utilisateur`` du diagramme de classes."""

from __future__ import annotations

from backend.security import ServiceAuthentification


class Utilisateur:
    """Un compte de l'application, avec son rôle.

    Le hash du mot de passe est privé : il ne se lit pas de l'extérieur, seule
    ``verifier_mot_de_passe()`` s'en sert (règle d'encapsulation de l'équipe).
    """

    ROLE_UTILISATEUR = "utilisateur"
    ROLE_SUPERVISEUR = "superviseur"
    ROLES = (ROLE_UTILISATEUR, ROLE_SUPERVISEUR)

    def __init__(self, email: str, mot_de_passe_hash: str, role: str) -> None:
        """Crée un utilisateur à partir des valeurs lues en base.

        Args:
            email: adresse qui sert d'identifiant de connexion.
            mot_de_passe_hash: hash bcrypt du mot de passe, jamais le mot de passe.
            role: « utilisateur » ou « superviseur ».
        """
        self.email = email
        self.role = role
        self._mot_de_passe_hash = mot_de_passe_hash

    def verifier_mot_de_passe(self, mot_de_passe: str) -> bool:
        """Indique si le mot de passe saisi est le bon."""
        return ServiceAuthentification.verifier_mot_de_passe(
            mot_de_passe, self._mot_de_passe_hash
        )

    def est_superviseur(self) -> bool:
        """Indique si ce compte a le rôle superviseur."""
        return self.role == self.ROLE_SUPERVISEUR
