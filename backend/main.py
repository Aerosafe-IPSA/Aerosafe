"""
Point d'entrée de l'API AeroSafe.
Initialise l'application FastAPI, crée les tables en base et définit les routes.
"""

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.dependencies import get_current_user, require_superviseur
from backend.models import Utilisateur
from backend.schemas import LoginRequest, TokenResponse, UtilisateurInfo
from backend.security import ServiceAuthentification

load_dotenv()

# Crée automatiquement les tables définies dans models.py si elles n'existent pas encore
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AeroSafe API")


@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authentifie un utilisateur et retourne un token JWT.
    Retourne 401 si l'email est inconnu ou le mot de passe incorrect.
    """
    user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()

    # On vérifie l'existance de l'utilisateur et la validité du mot de passe
    if not user or not ServiceAuthentification.verifier_mot_de_passe(data.mot_de_passe, user.mot_de_passe_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")

    return TokenResponse(access_token=ServiceAuthentification.creer_token(user.email, user.role))


@app.get("/me", response_model=UtilisateurInfo)
def me(user: UtilisateurInfo = Depends(get_current_user)):
    """Retourne les informations de l'utilisateur actuellement connecté."""
    return user


@app.get("/superviseur")
def route_superviseur(user: UtilisateurInfo = Depends(require_superviseur)):
    """Route accessible uniquement aux superviseurs (role = 'superviseur')."""
    return {"message": f"Bienvenue superviseur {user.email}"}
