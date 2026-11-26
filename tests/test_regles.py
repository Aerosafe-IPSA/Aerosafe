"""Tests des règles R1 à R5 et du moteur de règles."""

from datetime import datetime, timedelta, timezone

import pytest

from backend.rules.ecart_angulaire import ecart_angulaire
from backend.rules.moteur import MoteurRegles
from backend.rules.r1 import R1DelaiContact
from backend.rules.r2 import R2PositionAncienne
from backend.rules.r3 import R3VariationAltitude
from backend.rules.r4 import R4VariationVitesse
from backend.rules.r5 import R5ChangementCap
from collector.modeles import Aeronef, EtatVol

INSTANT = datetime(2026, 11, 24, 10, 0, tzinfo=timezone.utc)


def etat(**valeurs):
    """Fabrique un état de vol ordinaire, modifiable par mot-clé."""
    donnees = {
        "horodatage": INSTANT,
        "latitude": 44.0,
        "longitude": 0.2,
        "altitude": 9144.0,
        "vitesse": 228.0,
        "cap": 200.0,
        "taux_vertical": 0.0,
        "au_sol": False,
        "last_contact": INSTANT - timedelta(seconds=10),
        "time_position": INSTANT - timedelta(seconds=10),
    }
    donnees.update(valeurs)
    return EtatVol(**donnees)


def avion_avec(*etats):
    """Crée un aéronef avec les états donnés dans l'ordre."""
    a = Aeronef("39bd24", "AFR1462", "France")
    for e in etats:
        a.ajouter_etat(e)
    return a


# ---------------------------------------------------------------------------
# R1 — Délai de contact
# ---------------------------------------------------------------------------

def test_r1_cas_normal():
    a = avion_avec(etat(last_contact=INSTANT - timedelta(seconds=100)))
    assert R1DelaiContact().evaluer(a) is None


def test_r1_seuil_depasse():
    a = avion_avec(etat(last_contact=INSTANT - timedelta(seconds=400)))
    alerte = R1DelaiContact().evaluer(a)
    assert alerte.nom_regle == "R1"
    assert alerte.valeur_observee == pytest.approx(400.0)
    assert alerte.seuil == 300.0


def test_r1_valeur_manquante():
    a = avion_avec(etat(last_contact=None))
    assert R1DelaiContact().evaluer(a) is None


# ---------------------------------------------------------------------------
# R2 — Position ancienne
# ---------------------------------------------------------------------------

def test_r2_cas_normal():
    a = avion_avec(etat(time_position=INSTANT - timedelta(seconds=100)))
    assert R2PositionAncienne().evaluer(a) is None


def test_r2_seuil_depasse():
    a = avion_avec(etat(time_position=INSTANT - timedelta(seconds=700)))
    alerte = R2PositionAncienne().evaluer(a)
    assert alerte.nom_regle == "R2"
    assert alerte.valeur_observee == pytest.approx(700.0)
    assert alerte.seuil == 600.0


def test_r2_valeur_manquante():
    a = avion_avec(etat(time_position=None))
    assert R2PositionAncienne().evaluer(a) is None


# ---------------------------------------------------------------------------
# R3 — Variation d'altitude
# ---------------------------------------------------------------------------

def test_r3_cas_normal():
    a = avion_avec(etat(taux_vertical=-3.0))
    assert R3VariationAltitude().evaluer(a) is None


def test_r3_seuil_depasse():
    a = avion_avec(etat(taux_vertical=-18.4))
    alerte = R3VariationAltitude().evaluer(a)
    assert alerte.nom_regle == "R3"
    assert alerte.valeur_observee == pytest.approx(18.4)
    assert alerte.seuil == 15.0


def test_r3_valeur_manquante():
    a = avion_avec(etat(taux_vertical=None))
    assert R3VariationAltitude().evaluer(a) is None


# ---------------------------------------------------------------------------
# R4 — Variation de vitesse
# ---------------------------------------------------------------------------

def test_r4_cas_normal():
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=60)
    a = avion_avec(etat(horodatage=t1, vitesse=200.0), etat(horodatage=t2, vitesse=210.0))
    assert R4VariationVitesse().evaluer(a) is None


def test_r4_seuil_depasse():
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=60)
    a = avion_avec(etat(horodatage=t1, vitesse=100.0), etat(horodatage=t2, vitesse=160.0))
    alerte = R4VariationVitesse().evaluer(a)
    assert alerte.nom_regle == "R4"
    assert alerte.valeur_observee == pytest.approx(60.0)


def test_r4_une_seule_observation():
    a = avion_avec(etat(vitesse=200.0))
    assert R4VariationVitesse().evaluer(a) is None


def test_r4_valeur_manquante():
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=60)
    a = avion_avec(etat(horodatage=t1, vitesse=None), etat(horodatage=t2, vitesse=200.0))
    assert R4VariationVitesse().evaluer(a) is None


def test_r4_observations_trop_eloignees():
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=120)
    a = avion_avec(etat(horodatage=t1, vitesse=100.0), etat(horodatage=t2, vitesse=200.0))
    assert R4VariationVitesse().evaluer(a) is None


# ---------------------------------------------------------------------------
# R5 — Changement de cap
# ---------------------------------------------------------------------------

def test_r5_cas_normal():
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=60)
    a = avion_avec(etat(horodatage=t1, cap=200.0), etat(horodatage=t2, cap=210.0))
    assert R5ChangementCap().evaluer(a) is None


def test_r5_seuil_depasse():
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=60)
    a = avion_avec(etat(horodatage=t1, cap=100.0), etat(horodatage=t2, cap=200.0))
    alerte = R5ChangementCap().evaluer(a)
    assert alerte.nom_regle == "R5"
    assert alerte.valeur_observee == pytest.approx(100.0)


def test_r5_passage_350_a_10():
    """350° → 10° fait 20° d'écart, pas 340°."""
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=60)
    a = avion_avec(etat(horodatage=t1, cap=350.0), etat(horodatage=t2, cap=10.0))
    assert R5ChangementCap().evaluer(a) is None  # 20° < seuil 45°


def test_r5_une_seule_observation():
    a = avion_avec(etat(cap=200.0))
    assert R5ChangementCap().evaluer(a) is None


def test_r5_valeur_manquante():
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=60)
    a = avion_avec(etat(horodatage=t1, cap=None), etat(horodatage=t2, cap=200.0))
    assert R5ChangementCap().evaluer(a) is None


def test_r5_observations_trop_eloignees():
    t2 = INSTANT
    t1 = t2 - timedelta(seconds=120)
    a = avion_avec(etat(horodatage=t1, cap=100.0), etat(horodatage=t2, cap=200.0))
    assert R5ChangementCap().evaluer(a) is None


# ---------------------------------------------------------------------------
# ecart_angulaire
# ---------------------------------------------------------------------------

def test_ecart_angulaire_normal():
    assert ecart_angulaire(100.0, 160.0) == pytest.approx(60.0)


def test_ecart_angulaire_passage_zero():
    assert ecart_angulaire(350.0, 10.0) == pytest.approx(20.0)


def test_ecart_angulaire_oppose():
    assert ecart_angulaire(0.0, 180.0) == pytest.approx(180.0)


# ---------------------------------------------------------------------------
# MoteurRegles
# ---------------------------------------------------------------------------

def test_moteur_aucune_alerte():
    a = avion_avec(etat())
    assert MoteurRegles().analyser(a) == []


def test_moteur_detecte_r3():
    a = avion_avec(etat(taux_vertical=-20.0))
    alertes = MoteurRegles().analyser(a)
    noms = [al.nom_regle for al in alertes]
    assert "R3" in noms


def test_moteur_regles_par_defaut_cinq_regles():
    assert len(MoteurRegles.regles_par_defaut()) == 5


# ---------------------------------------------------------------------------
# Historique maximal
# ---------------------------------------------------------------------------

def test_historique_maximal():
    a = Aeronef("aaaaaa", None, None)
    for i in range(25):
        a.ajouter_etat(etat())
    assert len(a._historique) == Aeronef.HISTORIQUE_MAXIMAL
