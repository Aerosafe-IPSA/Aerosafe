"""Tests du collecteur OpenSky, sans appel réseau (l'API est simulée)."""

from unittest.mock import MagicMock

import pytest
import requests

from collector.__main__ import boucle
from collector.collecteur import CollecteurOpenSky, ErreurOpenSky
from collector.modeles import Aeronef, EtatVol

# Deux lignes au format OpenSky : 17 valeurs par aéronef
ETAT_COMPLET = [
    "39bd24",
    "AFR1462 ",
    "France",
    1762680000,
    1762680005,
    1.44,
    43.63,
    9144.0,
    False,
    228.0,
    200.0,
    -0.3,
    None,
    9200.0,
    "1000",
    False,
    0,
]
ETAT_INCOMPLET = [
    "3946e2",
    None,
    "France",
    None,
    1762679700,
    None,
    None,
    None,
    True,
    None,
    None,
    None,
    None,
    None,
    None,
    False,
    0,
]


def reponse(code=200, contenu=None, entetes=None):
    """Fabrique une fausse réponse HTTP."""
    rep = MagicMock(status_code=code, headers=entetes or {})
    rep.json.return_value = contenu
    return rep


def collecteur_avec(rep, **options):
    """Crée un collecteur dont la session HTTP renvoie ``rep``."""
    session = MagicMock()
    session.get.return_value = rep
    session.post.return_value = reponse(
        contenu={"access_token": "abc", "expires_in": 1800}
    )
    return CollecteurOpenSky(session=session, **options), session


def test_recuperer_etats_transforme_la_reponse():
    rep = reponse(contenu={"time": 1762680010, "states": [ETAT_COMPLET]})
    collecteur, _ = collecteur_avec(rep)

    aeronefs = collecteur.recuperer_etats()

    assert len(aeronefs) == 1
    avion = aeronefs[0]
    assert avion.icao24 == "39bd24"
    assert avion.callsign == "AFR1462"
    etat = avion.derniere_position()
    assert etat.altitude == 9144.0
    assert etat.vitesse == 228.0
    assert etat.cap == 200.0
    assert etat.au_sol is False
    assert etat.last_contact.timestamp() == 1762680005


def test_valeurs_manquantes_acceptees():
    rep = reponse(contenu={"time": 1762680010, "states": [ETAT_INCOMPLET]})
    collecteur, _ = collecteur_avec(rep)

    avion = collecteur.recuperer_etats()[0]

    assert avion.callsign is None
    etat = avion.derniere_position()
    assert etat.latitude is None
    assert etat.time_position is None
    assert etat.au_sol is True


def test_zone_vide():
    collecteur, _ = collecteur_avec(
        reponse(contenu={"time": 1762680010, "states": None})
    )
    assert collecteur.recuperer_etats() == []


def test_quota_depasse_leve_une_erreur():
    rep = reponse(429, entetes={"X-Rate-Limit-Retry-After-Seconds": "120"})
    collecteur, _ = collecteur_avec(rep)

    with pytest.raises(ErreurOpenSky, match="Quota"):
        collecteur.recuperer_etats()


def test_api_injoignable_leve_une_erreur():
    collecteur, session = collecteur_avec(None)
    session.get.side_effect = requests.ConnectionError("pas de réseau")

    with pytest.raises(ErreurOpenSky, match="injoignable"):
        collecteur.recuperer_etats()


def test_mode_anonyme_sans_jeton(monkeypatch):
    monkeypatch.delenv("OPENSKY_CLIENT_ID", raising=False)
    monkeypatch.delenv("OPENSKY_CLIENT_SECRET", raising=False)
    collecteur, session = collecteur_avec(reponse(contenu={"time": 1, "states": []}))

    collecteur.recuperer_etats()

    session.post.assert_not_called()
    assert session.get.call_args.kwargs["headers"] == {}


def test_jeton_oauth2_demande_une_seule_fois():
    rep = reponse(contenu={"time": 1, "states": []})
    collecteur, session = collecteur_avec(rep, client_id="id", client_secret="secret")

    collecteur.recuperer_etats()
    collecteur.recuperer_etats()

    assert session.post.call_count == 1
    assert session.get.call_args.kwargs["headers"] == {"Authorization": "Bearer abc"}


def test_recuperer_aeronef_par_icao24():
    rep = reponse(
        contenu={"time": 1762680010, "states": [ETAT_COMPLET, ETAT_INCOMPLET]}
    )
    collecteur, _ = collecteur_avec(rep)

    assert collecteur.recuperer_aeronef("39BD24").callsign == "AFR1462"
    assert collecteur.recuperer_aeronef("ffffff") is None


def test_historique_etat_precedent():
    avion = Aeronef("39bd24", "AFR1462", "France")
    premier = EtatVol.depuis_opensky(ETAT_COMPLET, 1762680010)
    second = EtatVol.depuis_opensky(ETAT_COMPLET, 1762680070)

    assert avion.etat_precedent() is None
    avion.ajouter_etat(premier)
    avion.ajouter_etat(second)

    assert avion.derniere_position() is second
    assert avion.etat_precedent() is premier


def test_boucle_continue_apres_une_erreur(monkeypatch):
    monkeypatch.setattr("collector.__main__.time.sleep", lambda _: None)
    collecteur = MagicMock()
    collecteur.recuperer_etats.side_effect = [ErreurOpenSky("quota"), []]

    boucle(collecteur, cycles=2)

    assert collecteur.recuperer_etats.call_count == 2
