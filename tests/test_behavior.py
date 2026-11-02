"""Behavioral, mathematical, and integration coverage beyond the starter tests."""

from copy import deepcopy
import json
import subprocess
import sys

import pytest

from src.evaluate import evaluate
from src.main import CATALOG
from src.profiles import PROFILES
from src.recommender import (STRATEGIES, load_songs, recommend_songs, score_song,
                             validate_preferences)
from src.reliability import check_output, reliable_recommend


@pytest.fixture
def songs():
    return load_songs(CATALOG)


def test_catalog_has_typed_attributes(songs):
    assert len(songs) == 24
    assert len({s["id"] for s in songs}) == 24
    assert all(isinstance(s["energy"], float) and isinstance(s["explicit"], bool) for s in songs)


def test_hand_calculated_score_and_explanation(songs):
    score, reasons = score_song(PROFILES["pop"], songs[0])
    assert score == pytest.approx(2 + 1 + (1 - abs(.82 - .8)))
    assert reasons == ["genre match (+2.000)", "mood match (+1.000)",
                       "energy 0.82 vs 0.8 (+0.980)"]


def test_energy_rewards_distance_not_high_values(songs):
    low = {**songs[0], "energy": .2}
    high = {**songs[0], "energy": .9}
    prefs = {**PROFILES["pop"], "energy": .2}
    assert score_song(prefs, low)[0] > score_song(prefs, high)[0]


@pytest.mark.parametrize("feature,target,far", [
    ("instrumentalness", .8, .1), ("popularity", 20, 95),
    ("release_year", 2000, 2050), ("duration_seconds", 180, 480),
    ("language", "spanish", "english"), ("valence", .9, .1),
    ("danceability", .8, .2), ("acousticness", .9, .1), ("tempo_bpm", 100, 200),
])
def test_optional_features_actually_affect_scores(songs, feature, target, far):
    prefs = {**PROFILES["pop"], feature: target}
    near_song = {**songs[0], feature: target}
    far_song = {**songs[0], feature: far}
    assert score_song(prefs, near_song)[0] > score_song(prefs, far_song)[0]


@pytest.mark.parametrize("mode", STRATEGIES)
@pytest.mark.parametrize("profile", PROFILES)
def test_profiles_modes_sorted_deterministic_nonmutating(songs, mode, profile):
    original = deepcopy(songs)
    first = recommend_songs(PROFILES[profile], songs, k=5, mode=mode, artist_penalty=.75)
    second = recommend_songs(PROFILES[profile], list(reversed(songs)), k=5, mode=mode, artist_penalty=.75)
    assert first == second
    assert songs == original
    assert [r[1] for r in first] == sorted([r[1] for r in first], reverse=True)
    assert len({r[0]["id"] for r in first}) == 5


def test_modes_can_reverse_a_ranking(songs):
    catalog = [{**songs[0], "id": 1, "genre": "pop", "mood": "sad", "energy": .8},
               {**songs[0], "id": 2, "genre": "rock", "mood": "happy", "energy": .8}]
    assert recommend_songs(PROFILES["pop"], catalog, mode="genre-first")[0][0]["id"] == 1
    assert recommend_songs(PROFILES["pop"], catalog, mode="mood-first")[0][0]["id"] == 2


def test_artist_penalty_changes_order_and_is_explained(songs):
    base = recommend_songs(PROFILES["pop"], songs, k=3)
    varied = recommend_songs(PROFILES["pop"], songs, k=3, artist_penalty=.75)
    assert [r[0]["id"] for r in base] == [11, 1, 12]
    assert [r[0]["id"] for r in varied] == [11, 12, 1]
    assert varied[2][1] == pytest.approx(base[1][1] - .75)
    assert "repeat artist penalty (-0.750)" in varied[2][2]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -.1, 1.1, True, "loud", None])
def test_invalid_energy_is_rejected(value):
    with pytest.raises(ValueError, match="energy"):
        validate_preferences({**PROFILES["pop"], "energy": value})


@pytest.mark.parametrize("prefs", [{}, [], {**PROFILES["pop"], "energi": .5},
                                  {**PROFILES["pop"], "mood": " "}])
def test_invalid_profile_structure_is_rejected(prefs):
    with pytest.raises(ValueError):
        validate_preferences(prefs)


@pytest.mark.parametrize("k", [0, -1, 1.5, True, 101])
def test_invalid_top_k_rejected_even_for_empty_catalog(k):
    with pytest.raises(ValueError, match="k"):
        recommend_songs(PROFILES["pop"], [], k=k)


def test_small_empty_and_tied_catalogs(songs):
    assert recommend_songs(PROFILES["pop"], []) == []
    tied = [{**songs[0], "id": 8}, {**songs[0], "id": 2}]
    assert [r[0]["id"] for r in recommend_songs(PROFILES["pop"], tied)] == [2, 8]


@pytest.mark.parametrize("change", [{"energy": "NaN"}, {"explicit": "maybe"},
                                    {"duration_seconds": 20.5}, {"title": ""}])
def test_corrupt_catalog_is_rejected(songs, change):
    with pytest.raises(ValueError, match="song 1"):
        recommend_songs(PROFILES["pop"], [{**songs[0], **change}])


def test_duplicate_ids_rejected(songs):
    with pytest.raises(ValueError, match="duplicate"):
        recommend_songs(PROFILES["pop"], [songs[0], songs[0]])


def test_malformed_csv_reports_schema_or_row_error(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("id,title\n1,Missing fields\n", encoding="utf-8")
    with pytest.raises(ValueError, match="headers"):
        load_songs(path)
    original = CATALOG.read_text(encoding="utf-8")
    path.write_text(original.replace("0.82,118", "broken,118", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="song 1: energy"):
        load_songs(path)


@pytest.mark.parametrize("corruption", ["score", "reasons", "duplicate", "foreign", "count", "order"])
def test_output_guard_rejects_corruption(songs, corruption):
    rows = recommend_songs(PROFILES["pop"], songs, k=3)
    song, score, reasons = rows[0]
    if corruption == "score":
        rows[0] = (song, score + 1, reasons)
    elif corruption == "reasons":
        rows[0] = (song, score, "invented reason")
    elif corruption == "duplicate":
        rows[1] = rows[0]
    elif corruption == "foreign":
        rows[0] = ({**song, "id": 999}, score, reasons)
    elif corruption == "count":
        rows.pop()
    else:
        rows.reverse()
    with pytest.raises(ValueError, match="output guardrail"):
        check_output(rows, songs, PROFILES["pop"], 3, "genre-first", 0)


def test_constraints_and_no_match_notice(songs):
    report = reliable_recommend(PROFILES["rock"], songs, clean_only=True, max_duration=225)
    assert all(not row[0]["explicit"] and row[0]["duration_seconds"] <= 225
               for row in report["recommendations"])
    empty = reliable_recommend(PROFILES["pop"], songs, max_duration=1)
    assert empty["recommendations"] == []
    assert "constraints were preserved" in empty["warnings"][-1]


def test_evaluation_suite_passes(songs):
    report = evaluate(songs)
    assert report["passed"] == report["total"] == 13, report


def test_cli_json_and_errors():
    result = subprocess.run([sys.executable, "-m", "src.main", "--profile", "edm", "--json"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["edm"]["recommendations"][0][0]["title"] == "Pulse Circuit"
    invalid = subprocess.run([sys.executable, "-m", "src.main", "--profile-file",
                              "examples/invalid_profile.json"], capture_output=True, text=True)
    assert invalid.returncode == 2
    assert "energy must be between 0 and 1" in invalid.stderr
    assert "Traceback" not in invalid.stderr
