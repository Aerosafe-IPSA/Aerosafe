"""
Dépendances FastAPI pour l'authentification et le contrôle d'accès par role.
Ces fonctions sont injectées dans les routes via Depends().
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from backend.security import decoder_token
from backend.schemas import UtilisateurInfo

# Indique à FastAPI où récuperer le token (utilisé pour la doc Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UtilisateurInfo:
    """
    Extrait et valide le token JWT depuis le header Authorization.
    Retourne les informations de l'utilisateur si le token est valide,
    sinon lève une erreur 401.
    """
    try:
        payload = decoder_token(token)
        return UtilisateurInfo(email=payload["sub"], role=payload["role"])
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )


def require_superviseur(user: UtilisateurInfo = Depends(get_current_user)) -> UtilisateurInfo:
    """
    Vérifie que l'utilisateur connecté a le role 'superviseur'.
    Lève une erreur 403 si ce n'est pas le cas.
    """
    if user.role != "superviseur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux superviseurs"
        )
    return user
