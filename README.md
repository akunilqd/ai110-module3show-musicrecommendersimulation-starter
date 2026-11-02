# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version, VibeFinder, recommends songs from a catalog of 24 fictional tracks. It compares song features with a listener's preferences, ranks the matches, and explains each result. It includes five listener profiles, three ranking modes, and an artist penalty for more variety. The Project 4 extension adds input validation, listening constraints, and checks that the results match the scoring rules.

---

## How The System Works

Real recommendation systems use input data such as song attributes and listening history to estimate what someone likes. Collaborative filtering finds patterns across listeners, while content-based filtering compares song features with a listener's preferences. Ranking then chooses which candidates to show. Spotify describes how listening, skipping, and saving songs influence its [recommendations](https://www.spotify.com/uk/safetyandprivacy/understanding-recommendations), and Google's [guide](https://developers.google.com/machine-learning/recommendation/overview/candidate-generation) explains the two filtering approaches. This simulation uses content-based rules and explicit preferences rather than learning from listening history.

- Each `Song` has a title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. Added attributes are instrumentalness, popularity, release year, duration, language, and an explicit-content flag. All tracks and values are synthetic.
- `UserProfile` stores favorite genre, favorite mood, target energy, and whether the listener likes acoustic music. The CLI's dictionary profiles also support optional targets for the other features.
- The default scoring rule gives 2 points for a genre match, 1 for a mood match, and `1 - abs(song_energy - target_energy)` for energy similarity. Optional numeric features also reward closeness to a target. Tempo has weight 1; other optional preferences have weight 0.5. The full ranges and distance scales are in the [model card](model_card.md).
- The recommender selects the highest-scoring remaining songs. The CLI subtracts 0.75 points for each earlier selection from the same artist and shows that penalty in the explanation. Genre-first, mood-first, and energy-first modes use different weights. Strong genre weighting can overlook songs that fit the listener's mood.

The Project 4 extension builds on this ranking process by validating inputs, filtering songs for clean-content or duration constraints, and checking scores and explanations before displaying results. The data flow is shown in the [architecture diagram](docs/architecture.mmd).

---

## Getting Started

### Setup

Use Python 3.10 or newer and run these commands from the repository folder.

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .\.venv\Scripts\Activate.ps1 # Windows PowerShell
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`. Additional behavior tests are in `tests/test_behavior.py`. Run the Project 4 evaluation harness with:

```bash
python -m src.evaluate
```

The current version passes 63 tests and all 13 evaluation cases.

---

## Sample Recommendation Output

These captured runs show the top five recommendations for pop, lofi, and rock listeners, including the reasons for each score.

<!-- BEGIN GENERATED SAMPLES -->

```console
$ python -m src.main --profile pop
Profile: pop | mode: genre-first | loaded: 24 | eligible: 24
#   Song / artist                              Score  Reasons
--------------------------------------------------------------------------------------------------------------------
1   Golden Hour / Neon Echo                    4.000  genre match (+2.000); mood match (+1.000); energy 0.8 vs 0.8
                                                      (+1.000)
2   Open Windows / Daylight Club               3.920  genre match (+2.000); mood match (+1.000); energy 0.72 vs
                                                      0.8 (+0.920)
3   Sunrise City / Neon Echo                   3.230  genre match (+2.000); mood match (+1.000); energy 0.82 vs
                                                      0.8 (+0.980); repeat artist penalty (-0.750)
4   Gym Hero / Max Pulse                       2.870  genre match (+2.000); mood mismatch (+0.000); energy 0.93 vs
                                                      0.8 (+0.870)
5   Barrio Sol / Luna Calle                    1.970  genre mismatch (+0.000); mood match (+1.000); energy 0.83 vs
                                                      0.8 (+0.970)
Output checks: passed
```

Exit status: 0.

```console
$ python -m src.main --profile lofi
Profile: lofi | mode: genre-first | loaded: 24 | eligible: 24
#   Song / artist                              Score  Reasons
--------------------------------------------------------------------------------------------------------------------
1   Quiet Pages / Paper Lanterns               5.475  genre match (+2.000); mood match (+1.000); energy 0.29 vs
                                                      0.3 (+0.990); tempo_bpm 74 vs 75 (+0.990); acousticness 0.91
                                                      vs 0.9 (+0.495)
2   Midnight Coding / LoRoom                   5.255  genre match (+2.000); mood match (+1.000); energy 0.42 vs
                                                      0.3 (+0.880); tempo_bpm 78 vs 75 (+0.970); acousticness 0.71
                                                      vs 0.9 (+0.405)
3   Library Rain / Paper Lanterns              4.650  genre match (+2.000); mood match (+1.000); energy 0.35 vs
                                                      0.3 (+0.950); tempo_bpm 72 vs 75 (+0.970); acousticness 0.86
                                                      vs 0.9 (+0.480); repeat artist penalty (-0.750)
4   Focus Flow / LoRoom                        3.540  genre match (+2.000); mood mismatch (+0.000); energy 0.4 vs
                                                      0.3 (+0.900); tempo_bpm 80 vs 75 (+0.950); acousticness 0.78
                                                      vs 0.9 (+0.440); repeat artist penalty (-0.750)
5   Spacewalk Thoughts / Orbit Bloom           3.320  genre mismatch (+0.000); mood match (+1.000); energy 0.28 vs
                                                      0.3 (+0.980); tempo_bpm 60 vs 75 (+0.850); acousticness 0.92
                                                      vs 0.9 (+0.490)
Output checks: passed
```

Exit status: 0.

```console
$ python -m src.main --profile rock
Profile: rock | mode: genre-first | loaded: 24 | eligible: 24
#   Song / artist                              Score  Reasons
--------------------------------------------------------------------------------------------------------------------
1   Iron Horizon / Voltline                    5.450  genre match (+2.000); mood match (+1.000); energy 0.96 vs
                                                      0.95 (+0.990); tempo_bpm 158 vs 155 (+0.970); acousticness
                                                      0.08 vs 0.1 (+0.490)
2   Wild Current / Granite Sky                 5.320  genre match (+2.000); mood match (+1.000); energy 0.88 vs
                                                      0.95 (+0.930); tempo_bpm 145 vs 155 (+0.900); acousticness
                                                      0.12 vs 0.1 (+0.490)
3   Storm Runner / Voltline                    4.680  genre match (+2.000); mood match (+1.000); energy 0.91 vs
                                                      0.95 (+0.960); tempo_bpm 152 vs 155 (+0.970); acousticness
                                                      0.1 vs 0.1 (+0.500); repeat artist penalty (-0.750)
4   Pulse Circuit / Prism Engine               3.285  genre mismatch (+0.000); mood match (+1.000); energy 0.97 vs
                                                      0.95 (+0.980); tempo_bpm 140 vs 155 (+0.850); acousticness
                                                      0.01 vs 0.1 (+0.455)
5   Gym Hero / Max Pulse                       3.225  genre mismatch (+0.000); mood match (+1.000); energy 0.93 vs
                                                      0.95 (+0.980); tempo_bpm 132 vs 155 (+0.770); acousticness
                                                      0.05 vs 0.1 (+0.475)
Output checks: passed
```

Exit status: 0.

<!-- END GENERATED SAMPLES -->

More profiles, ranking modes, and input/output guardrail demonstrations are in [docs/examples.md](docs/examples.md).

---

## Experiments You Tried

- Switching the pop profile to `energy-first` halves the genre weight and doubles the energy weight. The first three tracks stay in the same order, but Barrio Sol and Rooftop Lights take the last two spots instead of Gym Hero and Barrio Sol.
- Turning off the artist penalty gives Neon Echo both top spots for pop. With the penalty, Open Windows moves into second place and adds another artist.
- The lofi profile favors Quiet Pages for its chill mood, low energy, and slow tempo. The rock profile favors Iron Horizon for its intense mood and high energy. Pop instead favors Golden Hour's happy mood and matching energy.
- For Project 4, `--profile rock --clean-only --max-duration 225` changes the leader from Iron Horizon to Wild Current. An impossible duration limit returns no songs with a notice instead of ignoring the constraint. Invalid energy values are rejected before ranking.

Try the experiments with:

```bash
python -m src.main --profile pop --mode energy-first
python -m src.main --profile pop --artist-penalty 0
python -m src.main --profile rock --clean-only --max-duration 225
```

---

## Limitations and Risks

- The catalog is small and uneven: pop and lofi have more tracks than many other genres.
- Song attributes and content labels are synthetic. The system does not listen to audio or understand lyrics; language is only a matching label.
- Strong genre weights can narrow the results, while artist penalties improve variety without guaranteeing fairness.
- Passing the tests shows that the rules work as written, not that a listener will enjoy the playlist.

These limitations are discussed further in the [model card](model_card.md).

---

## Reflection

[**Model Card**](model_card.md)

The biggest takeaway from this project is how much a few scoring choices can change a recommendation. A song can move up because it matches someone's mood or move down because its artist already appeared. Seeing the points beside each result makes those choices easier to understand. The pop experiment also shows why it helps to look beyond the first result: changing the weights left the top three alone but changed the rest of the list.

AI helped build the code, expand the fictional catalog, and write tests. Keeping one shared scorer was useful because the rankings and explanations need to agree. The design moved away from separate scoring logic for the starter's two interfaces and left out unnecessary web interface dependencies. Those decisions are recorded in [ai_interactions.md](ai_interactions.md). If I continued the project, I would use a more varied catalog and collect listener feedback, because correct calculations do not tell us whether a playlist is enjoyable.
