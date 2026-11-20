import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def hasher_mot_de_passe(mot_de_passe: str) -> str:
    sel = bcrypt.gensalt()
    return bcrypt.hashpw(mot_de_passe.encode(), sel).decode()

def verifier_mot_de_passe(mot_de_passe: str, hash: str) -> bool:
    return bcrypt.checkpw(mot_de_passe.encode(), hash.encode())

def creer_token(email: str, role: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "role": role, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decoder_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])