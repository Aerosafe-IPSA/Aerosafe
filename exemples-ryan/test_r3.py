"""Exemple de tests pour une règle : cas normal, seuil dépassé, valeur manquante."""

from datetime import datetime, timezone

from backend.rules.r3 import R3VariationAltitude
from collector.modeles import Aeronef, EtatVol


def etat(**valeurs):
    """Fabrique un état de vol ordinaire, modifiable par mot-clé."""
    instant = datetime(2026, 11, 23, 14, 32, tzinfo=timezone.utc)
    donnees = {
        "horodatage": instant,
        "latitude": 44.0,
        "longitude": 0.2,
        "altitude": 9144.0,
        "vitesse": 228.0,
        "cap": 200.0,
        "taux_vertical": 0.0,
        "au_sol": False,
        "last_contact": instant,
        "time_position": instant,
    }
    donnees.update(valeurs)
    return EtatVol(**donnees)


def test_r3_seuil_depasse():
    avion = Aeronef("39bd24", "AFR1462", "France")
    avion.ajouter_etat(etat(taux_vertical=-18.4))

    alerte = R3VariationAltitude().evaluer(avion)

    assert alerte.nom_regle == "R3"
    assert alerte.valeur_observee == 18.4
    assert alerte.seuil == 15.0


def test_r3_cas_normal_et_valeur_manquante():
    avion = Aeronef("39bd24", "AFR1462", "France")
    avion.ajouter_etat(etat(taux_vertical=-3.0))
    assert R3VariationAltitude().evaluer(avion) is None
    avion.ajouter_etat(etat(taux_vertical=None))
    assert R3VariationAltitude().evaluer(avion) is None
