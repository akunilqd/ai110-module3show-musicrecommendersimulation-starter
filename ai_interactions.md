# AI Interactions and Development Decisions

## Actual task and workflow

The user supplied the five project phases and the Project 3 and Project 4 rubrics, and asked:

> follow the task and help me finish the repo; use git commit when needed

The coding assistant inspected the starter files and its tests, implemented the missing logic, expanded the dataset, ran the CLI and automated tests, added a reliability extension, captured reproducible outputs, and completed the technical documentation. The assistant used file reads/edits, Python commands, Git, and official recommendation-system sources linked in the README. No separate agents, real music API, model training, or hidden user listening data were used.

The following are reusable follow-up prompts that describe the workflow; they are **examples, not invented messages from the user**:

```text
Expand this fictional 10-song CSV to 24 songs. Preserve the starter rows,
add underrepresented genres, and add instrumentalness, popularity,
release_year, duration_seconds, language, and explicit. Keep numeric ranges
valid and clearly label every new value as synthetic.

Design interchangeable genre-first, mood-first, and energy-first weights.
Use numeric distance to reward closeness to the target. Generate the
explanation from the same contribution values used in the score.

Test conflicting preferences, unseen genres, invalid numeric values,
duplicate IDs, artist repetition, and impossible hard constraints.
Reject a fabricated explanation rather than presenting it as a valid result.
```

## Generated changes and design pattern

The assistant added 14 fictional songs and six attributes. Five new attributes participate in optional preference scoring, while explicit content is a hard constraint. The acoustic preset and custom JSON example exercise instrumentalness, popularity, release year, duration, and language together. Tests vary these features individually to confirm they change the score.

The chosen design pattern is **Strategy**. `RankingStrategy` instances in `src/recommender.py` supply distinct weights through `STRATEGIES`; `--mode` in `src/main.py` selects one. The assistant chose immutable weight configurations instead of three copies of the scoring function. This makes the experiment about preferences inspectable without allowing explanations to drift between modes. The original object-oriented interface delegates to the same dictionary scorer.

## Accepted and revised AI design choices

These are development decisions made by the coding assistant in this session, not claims of student approval:

| Choice | Decision and reason |
| --- | --- |
| Normalized distance rather than rewarding raw energy | Accepted: both high- and low-energy listeners need close matches. |
| Strategy pattern for ranking modes | Accepted: switchable weights preserve one scoring and explanation implementation. |
| Artist repetition penalty | Accepted with limits: expose the penalty and measure unique artists, without claiming demographic fairness. |
| Maintaining separate OOP and functional scoring implementations | Revised: delegate both starter interfaces to one engine to prevent inconsistent results. |
| Carrying pandas/Streamlit into the finished project | Rejected: CSV loading and formatted CLI output need only the standard library. |
| Treating every requested result count as mandatory | Revised: return fewer eligible tracks and a notice instead of violating listening constraints. |
| Calling the reliability workflow an autonomous agent or fine-tuned model | Rejected: it is a deterministic validate/filter/rank/check pipeline. |

## Verification notes

The assistant inspected the starter schema and preserved its original feature values, reviewed generated rows for range/plausibility, computed Sunrise City's base score by hand as 3.98, and compared observed mode/diversity changes against the formula. This is **AI-assisted review**, not an independent human audit of musical metadata. Numeric validity, CSV loading, score arithmetic, five extra scoring features, ranking stability, and guardrail failures are covered by tests. The behavioral harness output is committed in [docs/evaluation.json](docs/evaluation.json), and CLI results are captured in [docs/examples.md](docs/examples.md) and the README.

The student has not yet supplied personal listening judgments or manual verification notes. Before submission, they should run the commands, inspect the acoustic attribute choices and profile comparisons, and record any adjustments they actually make. Synthetic values must not be presented as measured Spotify data. No fabricated student actions or conversations have been inserted here.

## Project 4 workflow evidence

The runtime performs deterministic validation, filtering, ranking, and output checks. Its **observable stage events**, selected IDs, filter settings, and pass/fail status are recorded in [docs/audit_trace.json](docs/audit_trace.json). They are execution evidence, not private model reasoning or a claim of autonomous-agent tool calls. The report is generated by `python -m src.capture_examples` and is also available live with `python -m src.main --profile rock --clean-only --max-duration 225 --json`.

The baseline-to-guarded change is visible: Iron Horizon leads the unrestricted rock profile; Wild Current leads after clean-only and duration constraints. Empty eligible catalogs preserve constraints. The evaluator injects an invented reason and verifies rejection. No RAG or fine-tuning bonus is claimed; the implemented Project 4 stretch is the evaluation harness.

## Reflection

AI helped with the parts of this project that needed to fit together: the two starter interfaces, the scoring rules, the tests, and the examples in the documentation. But a suggestion still needed a way to check it. Adding more song attributes was only useful if those attributes actually affected the score. Adding an artist penalty was only useful if it changed who appeared in the results. The tests and captured runs make those changes visible. The next step would be getting feedback from listeners, because correct calculations alone cannot tell us whether a playlist is enjoyable.
