"""Distinct, reproducible taste profiles for the CLI and evaluation."""

PROFILES = {
    "pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3,
             "tempo_bpm": 75, "acousticness": 0.9},
    "rock": {"genre": "rock", "mood": "intense", "energy": 0.95,
             "tempo_bpm": 155, "acousticness": 0.1},
    "edm": {"genre": "edm", "mood": "intense", "energy": 0.95,
            "tempo_bpm": 140, "danceability": 0.95},
    "acoustic": {"genre": "folk", "mood": "relaxed", "energy": 0.25,
                 "acousticness": 0.95, "instrumentalness": 0.2,
                 "popularity": 25, "release_year": 2010,
                 "duration_seconds": 200, "language": "english"},
}
