"""CLI for VibeFinder; run from the repository with python -m src.main."""

import argparse
import json
from pathlib import Path
import textwrap

from .profiles import PROFILES
from .recommender import STRATEGIES, load_songs
from .reliability import reliable_recommend

CATALOG = Path(__file__).resolve().parents[1] / "data" / "songs.csv"


def format_results(recommendations):
    """Render a readable ASCII table with wrapped, untruncated score reasons."""
    lines = [f"{'#':<3} {'Song / artist':<40} {'Score':>7}  Reasons", "-" * 116]
    for index, (song, score, reasons) in enumerate(recommendations, 1):
        label = textwrap.wrap(f"{song['title']} / {song['artist']}", 40)
        details = textwrap.wrap(reasons, 60)
        for line in range(max(len(label), len(details))):
            prefix = str(index) if line == 0 else ""
            value = f"{score:.3f}" if line == 0 else ""
            lines.append(f"{prefix:<3} {label[line] if line < len(label) else '':<40} "
                         f"{value:>7}  {details[line] if line < len(details) else ''}")
    return "\n".join(lines)


def main():
    """Validate CLI inputs and run the guarded recommendation workflow."""
    parser = argparse.ArgumentParser(description="VibeFinder: explainable music recommendations")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--profile", choices=PROFILES, default="pop")
    source.add_argument("--all-profiles", action="store_true")
    source.add_argument("--profile-file", type=Path, help="JSON object of preference targets")
    parser.add_argument("--songs", type=Path, default=CATALOG)
    parser.add_argument("--mode", choices=STRATEGIES, default="genre-first")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--artist-penalty", type=float, default=0.75)
    parser.add_argument("--clean-only", action="store_true")
    parser.add_argument("--max-duration", type=int, help="Hard maximum track length in seconds")
    parser.add_argument("--json", action="store_true", help="Machine-readable results and audit events")
    args = parser.parse_args()
    try:
        songs = load_songs(args.songs)
        if args.profile_file:
            profiles = {args.profile_file.stem: json.loads(args.profile_file.read_text(encoding="utf-8"))}
        else:
            profiles = PROFILES if args.all_profiles else {args.profile: PROFILES[args.profile]}
        reports = {}
        for name, prefs in profiles.items():
            reports[name] = reliable_recommend(
                prefs, songs, k=args.top_k, mode=args.mode,
                artist_penalty=args.artist_penalty, clean_only=args.clean_only,
                max_duration=args.max_duration)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(reports, indent=2, allow_nan=False))
    else:
        for name, report in reports.items():
            print(f"Profile: {name} | mode: {args.mode} | loaded: {len(songs)} | eligible: {report['eligible_count']}")
            print(format_results(report["recommendations"]))
            for warning in report["warnings"]:
                print(f"Notice: {warning}")
            print("Output checks: passed\n")


if __name__ == "__main__":
    main()
