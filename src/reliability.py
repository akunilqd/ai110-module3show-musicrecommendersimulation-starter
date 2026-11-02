"""Project 4 extension: input, constraint, and output reliability gates."""

import math
from collections import Counter

from .recommender import (bounded_number, get_strategy, recommend_songs,
                          score_song, validate_catalog, validate_preferences)


def check_output(results, candidates, prefs, k, mode, artist_penalty):
    """Reject foreign/duplicate tracks, score drift, bad ordering, or false reasons."""
    catalog = {song["id"]: song for song in candidates}
    if len(results) != min(k, len(candidates)):
        raise ValueError("output guardrail: incorrect recommendation count")
    seen, counts, previous = set(), Counter(), math.inf
    for song, score, explanation in results:
        if song["id"] not in catalog or song != catalog[song["id"]] or song["id"] in seen:
            raise ValueError("output guardrail: foreign, altered, or duplicate track")
        base, reasons = score_song(prefs, song, mode)
        artist = song["artist"].casefold()
        cost = artist_penalty * counts[artist]
        expected_reasons = reasons + ([f"repeat artist penalty (-{cost:.3f})"] if cost else [])
        if not math.isfinite(score) or not math.isclose(score, base - cost, abs_tol=1e-9):
            raise ValueError("output guardrail: score does not match feature contributions")
        if score > previous + 1e-9 or explanation != "; ".join(expected_reasons):
            raise ValueError("output guardrail: ordering or explanation mismatch")
        previous = score
        seen.add(song["id"])
        counts[artist] += 1


def reliable_recommend(prefs, songs, k=5, mode="genre-first", artist_penalty=0.75,
                       clean_only=False, max_duration=None):
    """Validate, filter, rank, and check results without silently relaxing constraints."""
    prefs = validate_preferences(prefs)
    songs = validate_catalog(songs)
    k = bounded_number(k, "k", 1, 100, integer=True)
    artist_penalty = bounded_number(artist_penalty, "artist_penalty", 0, 10)
    get_strategy(mode)
    if not isinstance(clean_only, bool):
        raise ValueError("clean_only must be a boolean")
    if max_duration is not None:
        max_duration = bounded_number(max_duration, "max_duration", 1, 3600, integer=True)
    eligible = [song for song in songs
                if (not clean_only or not song["explicit"])
                and (max_duration is None or song["duration_seconds"] <= max_duration)]
    warnings = []
    if not any(song["genre"] == prefs["genre"] for song in eligible):
        warnings.append(f"No eligible songs match genre '{prefs['genre']}'; other features determine ranking.")
    if len(eligible) < k:
        warnings.append(f"Only {len(eligible)} eligible songs for top {k}; constraints were preserved.")
    results = recommend_songs(prefs, eligible, k, mode, artist_penalty)
    check_output(results, eligible, prefs, k, mode, artist_penalty)
    return {
        "recommendations": results, "eligible_count": len(eligible), "warnings": warnings,
        "audit": [
            {"stage": "validate", "status": "passed", "catalog_count": len(songs)},
            {"stage": "filter", "eligible_count": len(eligible), "clean_only": clean_only,
             "max_duration": max_duration},
            {"stage": "rank", "mode": mode, "artist_penalty": artist_penalty,
             "selected_ids": [row[0]["id"] for row in results]},
            {"stage": "output_check", "status": "passed"},
        ],
    }
