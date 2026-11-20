from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from backend.security import decoder_token
from backend.schemas import UtilisateurInfo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> UtilisateurInfo:
    try:
        payload = decoder_token(token)
        return UtilisateurInfo(email=payload["sub"], role=payload["role"])
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )

def require_superviseur(user: UtilisateurInfo = Depends(get_current_user)) -> UtilisateurInfo:
    if user.role != "superviseur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux superviseurs"
        )
    return user