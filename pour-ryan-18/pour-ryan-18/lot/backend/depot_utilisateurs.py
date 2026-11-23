"""Lecture et création des comptes dans la table ``app_user``."""

from __future__ import annotations

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from backend.bdd import BaseDeDonnees, UtilisateurTable
from backend.security import ServiceAuthentification
from backend.utilisateur import Utilisateur


class CompteExistantError(Exception):
    """Levée quand on crée un compte avec une adresse déjà utilisée."""


class DepotUtilisateurs:
    """Enregistre et retrouve les comptes ; le mot de passe n'est jamais stocké en clair."""

    def __init__(self, base: BaseDeDonnees) -> None:
        """Prépare le dépôt.

        Args:
            base: connexion à la base AeroSafe.
        """
        self._moteur = base.moteur

    @staticmethod
    def _normaliser(email: str) -> str:
        """Met l'adresse en minuscules, sans espaces autour."""
        return email.strip().lower()

    def trouver(self, email: str) -> Utilisateur | None:
        """Renvoie le compte qui correspond à cette adresse.

        Args:
            email: adresse saisie, sans tenir compte de la casse.

        Returns:
            L'utilisateur, ou None si aucun compte n'a cette adresse.
        """
        requete = select(UtilisateurTable).where(
            UtilisateurTable.email == self._normaliser(email)
        )
        with self._moteur.connect() as connexion:
            ligne = connexion.execute(requete).first()
        if ligne is None:
            return None
        return Utilisateur(ligne.email, ligne.mot_de_passe_hash, ligne.role)

    def creer(
        self, email: str, mot_de_passe: str, role: str = Utilisateur.ROLE_UTILISATEUR
    ) -> Utilisateur:
        """Crée un compte ; le mot de passe est haché avec bcrypt avant l'écriture.

        Args:
            email: adresse qui servira d'identifiant.
            mot_de_passe: mot de passe en clair, haché avant d'être enregistré.
            role: « utilisateur » ou « superviseur ».

        Returns:
            Le compte créé.

        Raises:
            ValueError: le rôle n'existe pas.
            CompteExistantError: un compte utilise déjà cette adresse.
        """
        if role not in Utilisateur.ROLES:
            raise ValueError(f"Rôle inconnu : {role} (attendu : {Utilisateur.ROLES})")
        adresse = self._normaliser(email)
        hash_mot_de_passe = ServiceAuthentification.hasher_mot_de_passe(mot_de_passe)
        try:
            with self._moteur.begin() as connexion:
                connexion.execute(
                    insert(UtilisateurTable).values(
                        email=adresse, mot_de_passe_hash=hash_mot_de_passe, role=role
                    )
                )
        except IntegrityError as erreur:
            raise CompteExistantError(
                f"Un compte existe déjà pour {adresse}"
            ) from erreur
        return Utilisateur(adresse, hash_mot_de_passe, role)
