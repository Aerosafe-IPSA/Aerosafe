"""Tests de la détection d'anomalies par IA, sur une base SQLite en mémoire."""

import pytest

from backend.bdd import BaseDeDonnees
from backend.detection_ia import (
    AnalyseIA,
    ComparaisonReglesIA,
    DetecteurAnomaliesIA,
    DonneesInsuffisantesError,
    LecteurObservations,
    ObservationAnalysee,
)
from collector.depot_positions import DepotPositions
from collector.modeles import Aeronef, EtatVol

T0 = 1762680000


def aeronef(icao24, horodatage, vitesse=230.0, cap=200.0, taux=0.0, altitude=10000.0):
    """Fabrique un aéronef avec un seul état, à l'instant donné."""
    etat = [
        icao24,
        "TEST",
        "France",
        horodatage - 2,
        horodatage - 1,
        1.44,
        43.63,
        altitude,
        False,
        vitesse,
        cap,
        taux,
        None,
        altitude,
        "1000",
        False,
        0,
    ]
    avion = Aeronef(icao24, "TEST", "France")
    avion.ajouter_etat(EtatVol.depuis_opensky(etat, horodatage))
    return avion


@pytest.fixture
def base():
    """Vingt vols ordinaires sur dix minutes, plus un vol en chute brutale."""
    base = BaseDeDonnees("sqlite://")
    depot = DepotPositions(base)
    for minute in range(10):
        instant = T0 + 60 * minute
        lot = [
            aeronef(
                f"aaa{i:03d}",
                instant,
                vitesse=220.0 + i,
                cap=(10.0 * i + minute) % 360,
                altitude=9000.0 + 100 * i,
            )
            for i in range(20)
        ]
        # bbb000 : vol stable, puis chute et forte décélération à la 9e minute
        chute = minute == 9
        lot.append(
            aeronef(
                "bbb000",
                instant,
                vitesse=120.0 if chute else 230.0,
                cap=95.0 if chute else 200.0,
                taux=-40.0 if chute else 0.0,
                altitude=6000.0 if chute else 10000.0,
            )
        )
        depot.enregistrer(lot)
    return base


def observation(**valeurs):
    """Fabrique une observation analysée ordinaire, modifiable par mot-clé."""
    donnees = {
        "icao24": "39bd24",
        "horodatage": None,
        "altitude": 10000.0,
        "vitesse": 230.0,
        "taux_vertical": 0.0,
        "variation_vitesse": 0.0,
        "variation_cap": 0.0,
        "silence": 1.0,
        "age_position": 2.0,
    }
    donnees.update(valeurs)
    return ObservationAnalysee(**donnees)


def test_ecart_angulaire_tient_compte_du_cercle():
    assert LecteurObservations.ecart_angulaire(350, 10) == 20
    assert LecteurObservations.ecart_angulaire(10, 350) == 20
    assert LecteurObservations.ecart_angulaire(90, 270) == 180


def test_regles_depassees():
    assert observation().regles_depassees() == []
    assert observation(silence=301).regles_depassees() == ["R1"]
    assert observation(age_position=601).regles_depassees() == ["R2"]
    assert observation(taux_vertical=-16).regles_depassees() == ["R3"]
    assert observation(variation_vitesse=52).regles_depassees() == ["R4"]
    assert observation(variation_cap=46).regles_depassees() == ["R5"]


def test_lecture_calcule_les_variations(base):
    observations = LecteurObservations(base).lire()

    assert len(observations) == 210
    derniere = [o for o in observations if o.icao24 == "bbb000"][-1]
    assert derniere.variation_vitesse == pytest.approx(110.0)
    assert derniere.variation_cap == pytest.approx(105.0)
    assert derniere.regles_depassees() == ["R3", "R4", "R5"]


def test_le_modele_repere_le_vol_atypique(base):
    classement = AnalyseIA(base).plus_atypiques(1)

    plus_atypique, score = classement[0]
    assert plus_atypique.icao24 == "bbb000"
    assert plus_atypique.regles_depassees() == ["R3", "R4", "R5"]
    assert 0.5 < score <= 1


def test_comparaison_avec_les_regles(base):
    bilan = AnalyseIA(base).comparer()

    assert bilan.total == 210
    assert bilan.regles_et_ia == 1
    assert bilan.regles_seules == 0
    assert (
        bilan.regles_et_ia + bilan.regles_seules + bilan.ia_seule + bilan.aucune == 210
    )
    assert bilan.part_des_regles_retrouvee == 1.0
    assert "Taux d'accord" in bilan.resume()


def test_resultat_reproductible(base):
    assert AnalyseIA(base).comparer() == AnalyseIA(base).comparer()


def test_donnees_insuffisantes():
    with pytest.raises(DonneesInsuffisantesError, match="au moins 50"):
        AnalyseIA(BaseDeDonnees("sqlite://")).comparer()


def test_prediction_refusee_avant_entrainement():
    with pytest.raises(RuntimeError, match="entraîné"):
        DetecteurAnomaliesIA().scores([observation()])


def test_bilan_vide():
    bilan = ComparaisonReglesIA(0, 0, 0, 0)

    assert bilan.taux_accord == 0.0
    assert bilan.part_des_regles_retrouvee == 0.0
