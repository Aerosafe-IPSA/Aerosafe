"""
Sécurité de l'application : hashage bcrypt et gestion des tokens JWT.
Toutes les opérations sont regroupées dans ServiceAuthentification pour
respecter le principe de responsabilité unique (SRP).
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt


class ConfigurationManquanteError(Exception):
    """Levée quand JWT_SECRET n'est pas défini dans le fichier .env."""


class ServiceAuthentification:
    """Regroupe le hashage de mots de passe et la gestion des tokens JWT."""

    @staticmethod
    def hasher_mot_de_passe(mot_de_passe: str) -> str:
        """Hash un mot de passe avec bcrypt (sel aléatoire à chaque appel)."""
        sel = bcrypt.gensalt()
        return bcrypt.hashpw(mot_de_passe.encode(), sel).decode()

    @staticmethod
    def verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
        """Retourne True si le mot de passe correspond au hash stocké en base."""
        return bcrypt.checkpw(mot_de_passe.encode(), hash_stocke.encode())

    @staticmethod
    def _secret() -> str:
        """Lit la clé de signature des tokens, obligatoire."""
        secret = os.getenv("JWT_SECRET")
        if not secret:
            raise ConfigurationManquanteError(
                "JWT_SECRET est absent : ajoute-le dans le fichier .env (voir .env.example)"
            )
        return secret

    @classmethod
    def creer_token(cls, email: str, role: str) -> str:
        """Génère un token JWT signé (payload : sub, role, exp)."""
        algorithme = os.getenv("JWT_ALGORITHM", "HS256")
        duree = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        expiration = datetime.now(timezone.utc) + timedelta(minutes=duree)
        payload = {"sub": email, "role": role, "exp": expiration}
        return jwt.encode(payload, cls._secret(), algorithm=algorithme)

    @classmethod
    def decoder_token(cls, token: str) -> dict:
        """Décode et vérifie un token JWT. Lève PyJWTError si invalide ou expiré."""
        algorithme = os.getenv("JWT_ALGORITHM", "HS256")
        return jwt.decode(token, cls._secret(), algorithms=[algorithme])
