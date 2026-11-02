"""Run fixed behavioral expectations without external services or pytest."""

import argparse
import json
from pathlib import Path

from .main import CATALOG
from .profiles import PROFILES
from .recommender import load_songs, recommend_songs
from .reliability import check_output, reliable_recommend


def require(condition, message):
    """Fail an evaluation even when Python runs with optimizations enabled."""
    if not condition:
        raise ValueError(message)


def evaluate(songs):
    """Evaluate profile relevance, diversity, constraints, and rejection behavior."""
    cases = []

    def run(name, operation):
        """Record failures and continue so the summary covers every case."""
        try:
            detail = operation()
            cases.append({"case": name, "passed": True, "detail": detail})
        except Exception as error:
            cases.append({"case": name, "passed": False, "detail": str(error)})

    def top_track(profile, expected):
        report = reliable_recommend(PROFILES[profile], songs, k=3)
        rows = report["recommendations"]
        require(rows[0][0]["title"] == expected, f"expected {expected}")
        require(len(rows) == 3, "expected three results")
        require(all(a[1] >= b[1] for a, b in zip(rows, rows[1:])), "scores not sorted")
        return f"top track = {expected}; 3 sorted recommendations"

    for profile, title in [("pop", "Golden Hour"), ("lofi", "Quiet Pages"),
                           ("rock", "Iron Horizon"), ("edm", "Pulse Circuit"),
                           ("acoustic", "Porchlight Letter")]:
        run(profile, lambda p=profile, t=title: top_track(p, t))

    def diversity():
        base = recommend_songs(PROFILES["pop"], songs, k=2)
        varied = reliable_recommend(PROFILES["pop"], songs, k=2)["recommendations"]
        before = len({r[0]["artist"] for r in base})
        after = len({r[0]["artist"] for r in varied})
        require((before, after) == (1, 2), "artist exposure did not improve")
        return "top-2 unique artists: 1 -> 2"

    run("artist diversity", diversity)

    def clean():
        base = reliable_recommend(PROFILES["rock"], songs, k=3)["recommendations"]
        report = reliable_recommend(PROFILES["rock"], songs, k=3, clean_only=True,
                                    max_duration=225)
        rows = report["recommendations"]
        require(any(r[0]["explicit"] for r in base), "baseline should include an explicit track")
        require(len(rows) == 3 and all(not r[0]["explicit"] and r[0]["duration_seconds"] <= 225
                                      for r in rows), "hard constraint violated")
        require(rows[0][0]["title"] == "Wild Current", "expected changed top track")
        return "explicit tracks removed; all durations <= 225; top = Wild Current"

    run("clean and short", clean)

    def empty():
        report = reliable_recommend(PROFILES["pop"], songs, max_duration=1)
        require(not report["recommendations"] and report["warnings"], "empty result must explain why")
        return "0 results; constraints preserved with a notice"

    run("no eligible tracks", empty)

    def unknown():
        report = reliable_recommend({"genre": "unlisted", "mood": "happy", "energy": 0.8}, songs)
        require(report["warnings"] and len(report["recommendations"]) == 5, "missing fallback notice")
        return "5 results from remaining preferences; missing-genre notice"

    run("unknown genre", unknown)

    def rejected(prefs):
        try:
            reliable_recommend(prefs, songs)
        except ValueError as error:
            return f"rejected: {error}"
        raise ValueError("invalid profile was accepted")

    run("out-of-range energy", lambda: rejected({**PROFILES["pop"], "energy": 1.5}))
    run("nonfinite energy", lambda: rejected({**PROFILES["pop"], "energy": float("nan")}))
    run("misspelled preference", lambda: rejected({**PROFILES["pop"], "energi": 0.2}))

    def corruption():
        rows = recommend_songs(PROFILES["pop"], songs, k=3)
        song, score, _ = rows[0]
        rows[0] = (song, score, "This song is popular, so you will like it.")
        try:
            check_output(rows, songs, PROFILES["pop"], 3, "genre-first", 0)
        except ValueError as error:
            return f"rejected: {error}"
        raise ValueError("fabricated explanation was accepted")

    run("fabricated explanation", corruption)
    return {"passed": sum(case["passed"] for case in cases), "total": len(cases), "cases": cases}


def main():
    """Print pass/fail results and optionally write a reproducible JSON report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = evaluate(load_songs(CATALOG))
    for case in report["cases"]:
        print(f"{'PASS' if case['passed'] else 'FAIL'} {case['case']}: {case['detail']}")
    print(f"Evaluation: {report['passed']}/{report['total']} passed")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
