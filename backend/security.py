"""
Fonctions de sécurité : hashage bcrypt des mots de passe et gestion des tokens JWT.
"""

import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone

# Variables lues depuis le .env (chargé par database.py en premier)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def hasher_mot_de_passe(mot_de_passe: str) -> str:
    """
    Hash un mot de passe en clair avec bcrypt.
    bcrypt génère un sel aléatoire à chaque appel, donc deux hash du même mot de passe
    seront toujours différents.
    """
    sel = bcrypt.gensalt()
    return bcrypt.hashpw(mot_de_passe.encode(), sel).decode()


def verifier_mot_de_passe(mot_de_passe: str, hash: str) -> bool:
    """Compare un mot de passe saisi avec le hash stocké en base."""
    return bcrypt.checkpw(mot_de_passe.encode(), hash.encode())


def creer_token(email: str, role: str) -> str:
    """
    Génère un token JWT signé contenant l'email, le role et une date d'expiration.
    Le token est signé avec JWT_SECRET — toute modification du token invalide la signature.
    """
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "role": role, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decoder_token(token: str) -> dict:
    """
    Décode et vérifie un token JWT.
    Lève une exception PyJWTError si le token est invalide ou expiré.
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
