# Model Card: VibeFinder 1.0

## Goal, intended use, and non-intended use

VibeFinder suggests songs whose annotated attributes match an explicit taste profile. It is a classroom simulation for understanding content-based ranking, explanation, diversity, and reliability. The Project 4 extension adds validated inputs, hard listening constraints, output checks, and a fixed behavioral evaluation suite to the Project 3 recommender. It is not a trained predictor, production streaming service, content moderation system, or measure of musical quality. Clean-content labels are synthetic; they cannot certify real songs as suitable for children.

## Data and attributes

The catalog has **24 fictional songs across 14 genre labels**. Rows 1–10 come from the starter; rows 11–24 and the six new attribute columns were generated during AI-assisted development. There are no audio files, real play counts, user records, or scraped lyrics. The original numeric attributes were retained for the starter tracks. All values should be interpreted as simulation data, not verified facts about real recordings.

| Attribute | Meaning and validation | Scoring use |
| --- | --- | --- |
| id, title, artist | Unique positive integer ID; nonempty title/artist | ID breaks ties; artist identifies repetition |
| genre, mood | Nonempty categorical labels | Exact match, case-insensitive |
| energy | Intensity, 0–1 | Distance to required target |
| tempo_bpm | Tempo, 20–300 | Optional distance / 100 |
| valence | Positive affect, 0–1 | Optional distance / 1 |
| danceability | Dance suitability, 0–1 | Optional distance / 1 |
| acousticness | Acoustic character, 0–1 | Optional distance / 1 |
| instrumentalness (new) | Instrumental character, 0–1 | Optional distance / 1 |
| popularity (new) | Synthetic popularity, 0–100 | Optional distance / 100; does not always reward popularity |
| release_year (new) | Integer year, 1900–2100 | Optional distance / 50; allowed range is a schema bound |
| duration_seconds (new) | Integer seconds, 1–3600 | Optional distance / 300; also a hard maximum filter |
| language (new) | Nonempty label; `instrumental` means no lyrics in this catalog | Optional exact match |
| explicit (new) | CSV `true` or `false` | Hard filter with `--clean-only` |

Input profiles require genre, mood, and energy; omitted optional attributes add no points. CSV headers must match the documented schema. Duplicate IDs, missing cells, malformed numeric values, NaN/infinity, and unknown preference names are rejected. Categorical preference values need not already exist in the catalog, allowing honest fallback to other features.

## Algorithm summary

First, compare each song against the supplied preferences. Matching genre and mood earn points; a numeric attribute earns more points the closer it is to its target. Clip numeric similarities at zero so a very distant song never earns negative feature points. Add those contributions to produce a base score. Genre-first weights genre/mood/energy as 2/1/1; mood-first uses 0.5/3/1; energy-first uses 1/1/2. Tempo weighs 1 and other optional features weigh 0.5. These hand-chosen weights were not fitted to listener ratings.

Next, repeatedly select the best remaining song. If its artist has already appeared, subtract the configured cost per prior appearance before comparing candidates. Equal scores use the lower song ID. The default CLI artist penalty is 0.75; the base functional API defaults to zero for ordinary ranking. Negative adjusted scores are possible with large penalties; they mean an exposure tradeoff, not negative enjoyment. Displayed explanations are generated directly from the same feature contributions and penalty. They may differ by 0.001 from a sum of displayed values because each value is rounded for readability.

Finally, the Project 4 wrapper checks that all output tracks belong to the eligible catalog, that IDs are unique, that count and order are valid, and that each score and reason agrees with the supplied profile and accumulated artist penalty. It records stage outcomes for inspection. The checker reuses the feature scorer, so a common bug in that scorer could escape it; hand-calculated tests provide an additional check. It verifies consistency, not real-world taste accuracy or the global optimality of a playlist.

## Strengths and observed behavior

Explicit preferences cause reproducible changes. The pop profile selects Golden Hour first (4.000); lofi selects Quiet Pages (5.475); rock selects Iron Horizon (5.450); EDM selects Pulse Circuit (5.475); acoustic selects Porchlight Letter (6.940). These scores have different maxima because profiles enable different attributes. The top-five runs and all explanations for pop, lofi, and rock appear as text in [README.md](README.md#sample-recommendation-output); the other two profiles are in [docs/examples.md](docs/examples.md).

For three concrete explanations: Golden Hour earns 2 genre points, 1 mood point, and 1 energy point because its energy exactly matches 0.8. Quiet Pages earns 2 genre points, 1 mood point, 0.990 for energy, 0.990 for tempo, and 0.495 for acousticness. Iron Horizon earns 2 genre points, 1 mood point, 0.990 for energy, 0.970 for tempo, and 0.490 for acousticness. These are actual scoring contributions, not generated claims about how the songs sound.

### Profile comparisons

| Pair | Observed difference and explanation |
| --- | --- |
| Pop / lofi | Golden Hour versus Quiet Pages: happy pop and 0.8 energy shift to chill lofi, about 75 BPM and low energy. |
| Pop / rock | Golden Hour versus Iron Horizon: rock genre, intense mood, and fast tempo replace happy pop preferences. |
| Lofi / rock | Quiet Pages versus Iron Horizon: acoustic, slow, low-energy targets oppose the rock profile's fast, intense targets. |
| Pop / EDM | Golden Hour versus Pulse Circuit: EDM adds fast tempo and high danceability and requests intense mood. |
| Pop / acoustic | Golden Hour versus Porchlight Letter: relaxed folk, low energy and high acousticness replace bright pop. |
| Lofi / EDM | Quiet Pages versus Pulse Circuit: low tempo and acousticness preference shift to fast, danceable tracks. |
| Lofi / acoustic | Quiet Pages versus Porchlight Letter: both favor low energy, but acoustic explicitly favors folk, English lyrics, an older year and lower popularity. |
| Rock / EDM | Iron Horizon versus Pulse Circuit: both favor high energy and intense mood, but genre and danceability distinguish them. |
| Rock / acoustic | Iron Horizon versus Porchlight Letter: intense, fast, low-acousticness preferences shift to quiet acoustic folk. |
| EDM / acoustic | Pulse Circuit versus Porchlight Letter: energetic dance targets shift to relaxed folk and low-energy targets. |

## Evaluation and sensitivity experiment

Run `python -m pytest -q` for automated tests and `python -m src.evaluate` for the behavioral harness. Tests cover both starter interfaces, scoring arithmetic, every extra scored feature, all mode/profile combinations, stable ties, input validation, diversity penalties, corrupted outputs, and CLI behavior. The harness checks five expected leaders, increased artist variety, clean/short constraints, empty eligibility, unseen genres, three invalid inputs, and an invented explanation. It passes **13/13 fixed cases**; the committed report is [docs/evaluation.json](docs/evaluation.json). These cases were designed alongside the implementation; they are regression checks, not a held-out human-rating study.

With the pop profile, switching from genre-first to energy-first halves genre weight and doubles energy weight. Captured top-five scores are:

| Position | Genre-first | Energy-first |
| --- | --- | --- |
| 1 | Golden Hour, 4.000 | Golden Hour, 4.000 |
| 2 | Open Windows, 3.920 | Open Windows, 3.840 |
| 3 | Sunrise City, 3.230 | Sunrise City, 3.210 |
| 4 | Gym Hero, 2.870 | Barrio Sol, 2.940 |
| 5 | Barrio Sol, 1.970 | Rooftop Lights, 2.920 |

Gym Hero has the requested genre but the wrong mood and energy 0.93. Barrio Sol and Rooftop Lights have the requested happy mood and energy closer to 0.8, so they become more competitive after the weight shift. The unchanged first three show that a parameter change need not reorder every item. This demonstrates sensitivity, not proven improvement. Artist diversity increases from one artist to two in the pop top two when the penalty changes from 0 to 0.75. It can promote another artist without inventing a reason for preference similarity.

For the Project 4 extension, unrestricted rock selects explicit Iron Horizon first; clean-only with maximum duration 225 seconds selects Wild Current instead. A one-second limit returns zero tracks with a notice. Energy 1.5 is rejected before ranking. A deliberately fabricated output explanation is rejected by the output checker. [Captured demonstrations](docs/examples.md#guardrail-demonstrations) include input, output, and exit status.

## Limitations and bias

The catalog is small and uneven: pop and lofi each have four tracks, rock has three, while many genres have only one. Exact labels treat `pop` and `indie pop` as unrelated, and broad labels such as `world` erase meaningful musical distinctions. Mood and energy values are subjective annotations with no audio verification, so the system can consistently rank incorrect metadata. English lyrics dominate the vocal examples; language preferences can further narrow exposure, and an optional popularity target can reproduce popularity bias. Artist penalties improve exposure variety within this catalog but do not guarantee genre, language, cultural, or demographic fairness and may lower preference fit.

There is no memory of skips, changing taste, or listening context. The ranker is greedy, not an optimizer for an entire playlist. Guardrails trust synthetic explicit labels and cannot detect mislabeled real content. Reliability checks enforce stated rules but cannot determine whether a recommendation feels right to a listener.

## Improvement ideas

1. Gather consented listener ratings and compare ranking quality and exposure diversity on held-out profiles.
2. Expand the catalog with balanced genre/language coverage and reviewed metadata; support multiple genre and mood tags.
3. Learn feature weights from feedback and measure the quality/diversity tradeoff instead of choosing a universal artist penalty.

## Development reflection

Building this simulation illustrates how a simple numeric distance can create plausible recommendations without understanding music. The most useful design choice was making score contributions the source of explanations: this makes weight changes inspectable and exposes a repeated-artist penalty directly. The unexpected pattern in the pop experiment is that changing two weights leaves the first three results stable while changing the tail of the list. Checking only the first recommendation would have missed that behavior.

AI assistance produced the implementation and suggested the synthetic attributes and Strategy pattern. A separate implementation for the object and dictionary APIs was revised into one shared scorer, and unnecessary web/UI dependencies were removed to keep the simulation easy to reproduce. Automated checks caught behavior risks through invalid inputs and deliberately corrupted results; they do not replace a person's judgment of musical relevance. Next development work should collect human feedback rather than assume that passing arithmetic tests proves recommendation quality.

This reflection records the AI-assisted engineering work, not a claim about the student's personal experience. Student review and a personal account of what they learned are still appropriate before submission. See [the interaction log](ai_interactions.md) for provenance and verification boundaries.
