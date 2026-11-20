from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from backend.database import engine, Base, get_db
from backend.models import Utilisateur
from backend.security import hasher_mot_de_passe, verifier_mot_de_passe, creer_token
from backend.schemas import LoginRequest, TokenResponse, UtilisateurInfo
from backend.dependencies import get_current_user, require_superviseur

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AeroSafe API")

@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
    if not user or not verifier_mot_de_passe(data.mot_de_passe, user.mot_de_passe_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
    return TokenResponse(access_token=creer_token(user.email, user.role))

@app.get("/me", response_model=UtilisateurInfo)
def me(user: UtilisateurInfo = Depends(get_current_user)):
    return user

@app.get("/superviseur")
def route_superviseur(user: UtilisateurInfo = Depends(require_superviseur)):
    return {"message": f"Bienvenue superviseur {user.email}"}