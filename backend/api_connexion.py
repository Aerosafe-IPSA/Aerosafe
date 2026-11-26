"""Routes de connexion et contrôle d'accès par jeton et par rôle."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError

from backend.depot_utilisateurs import DepotUtilisateurs
from backend.schemas import LoginRequest, TokenResponse, UtilisateurInfo
from backend.security import ServiceAuthentification
from backend.utilisateur import Utilisateur

# Lit l'en-tête « Authorization: Bearer <jeton> » ; ajoute le bouton Authorize dans /docs
SCHEMA_JETON = HTTPBearer(auto_error=False, description="Jeton renvoyé par POST /login")


class GardeAcces:
    """Vérifie le jeton d'une requête et, si demandé, le rôle de son auteur.

    Ses méthodes ``verifier`` s'utilisent comme dépendances FastAPI pour protéger
    une route ou un routeur entier.
    """

    def __init__(self, role_exige: Optional[str] = None) -> None:
        """Prépare la garde.

        Args:
            role_exige: rôle obligatoire pour passer ; None pour tout compte connecté.
        """
        self._role_exige = role_exige

    def verifier(
        self,
        request: Request,
        jeton: Optional[HTTPAuthorizationCredentials] = Depends(SCHEMA_JETON),
    ) -> UtilisateurInfo:
        """Renvoie l'utilisateur connecté, ou refuse la requête.

        Raises:
            HTTPException: 401 sans jeton valide, 403 si le rôle ne suffit pas.
        """
        if jeton is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Connexion requise"
            )
        try:
            contenu = ServiceAuthentification.decoder_token(jeton.credentials)
            utilisateur = UtilisateurInfo(email=contenu["sub"], role=contenu["role"])
        except (PyJWTError, KeyError) as erreur:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré",
            ) from erreur
        if self._role_exige is not None and utilisateur.role != self._role_exige:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux superviseurs",
            )
        request.state.utilisateur = utilisateur
        return utilisateur


class ApiConnexion:
    """Expose la connexion (``/login``) et les routes qui dépendent du compte connecté."""

    def __init__(self, depot: DepotUtilisateurs) -> None:
        """Déclare les routes.

        Args:
            depot: le dépôt qui lit les comptes en base.
        """
        self._depot = depot
        self._garde = GardeAcces()
        self._garde_superviseur = GardeAcces(Utilisateur.ROLE_SUPERVISEUR)
        self._routeur = APIRouter(tags=["Connexion"])
        self._routeur.add_api_route(
            "/login",
            self.connecter,
            methods=["POST"],
            response_model=TokenResponse,
            summary="Se connecter et recevoir un jeton",
        )
        self._routeur.add_api_route(
            "/me",
            self.moi,
            methods=["GET"],
            response_model=UtilisateurInfo,
            dependencies=[Depends(self._garde.verifier)],
            summary="Compte actuellement connecté",
        )
        self._routeur.add_api_route(
            "/superviseur",
            self.espace_superviseur,
            methods=["GET"],
            dependencies=[Depends(self._garde_superviseur.verifier)],
            summary="Route réservée aux superviseurs",
        )

    @property
    def routeur(self) -> APIRouter:
        """Routeur FastAPI à brancher sur l'application."""
        return self._routeur

    @property
    def garde(self) -> GardeAcces:
        """Garde qui exige un compte connecté, pour protéger les autres routes."""
        return self._garde

    @property
    def garde_superviseur(self) -> GardeAcces:
        """Garde qui exige le rôle superviseur."""
        return self._garde_superviseur

    def connecter(self, donnees: LoginRequest) -> TokenResponse:
        """Authentifie un utilisateur et retourne un token JWT.

        Retourne 401 si l'email est inconnu ou le mot de passe incorrect, sans
        préciser lequel des deux est faux.
        """
        utilisateur = self._depot.trouver(donnees.email)
        if utilisateur is None or not utilisateur.verifier_mot_de_passe(
            donnees.mot_de_passe
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants invalides",
            )
        jeton = ServiceAuthentification.creer_token(utilisateur.email, utilisateur.role)
        return TokenResponse(access_token=jeton)

    def moi(self, request: Request) -> UtilisateurInfo:
        """Retourne les informations de l'utilisateur actuellement connecté."""
        return request.state.utilisateur

    def espace_superviseur(self, request: Request) -> dict:
        """Route accessible uniquement aux superviseurs (role = 'superviseur')."""
        return {"message": f"Bienvenue superviseur {request.state.utilisateur.email}"}
