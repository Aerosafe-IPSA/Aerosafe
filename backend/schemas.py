"""
Schémas Pydantic pour la validation des données entrantes et sortantes de l'API.
Pydantic vérifie automatiquement les types et formats avant que le code s'exécute.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Données attendues dans le body de la requête POST /login."""

    email: EmailStr  # Pydantic vérifie que c'est bien un email valide
    mot_de_passe: str


class TokenResponse(BaseModel):
    """Réponse renvoyée après un login réussi."""

    access_token: str
    token_type: str = "bearer"  # Toujours "bearer" pour les JWT


class UtilisateurInfo(BaseModel):
    """Informations de l'utilisateur courant, extraites du token JWT."""

    email: str
    role: str
