# Sentiment analysis on customer reviews — WeLoveReviews

Harbor House Café, 500 service reviews. The business question is whether the written sentiment matches a **4.5 / 5** average.

`src/explore.ipynb` is the analysis (Spanish, saved with executed outputs). `src/app.py` is the production path: one load of a pinned Hugging Face model, then a CSV.

## Result

Same bands on both rows: 1–2 negative, 3 neutral, 4–5 positive. The human mean of this file is the stated 4.5.

| Source | Positive (4–5) | Neutral (3) | Negative (1–2) | Mean stars |
| --- | --- | --- | --- | --- |
| Human rating | 86.4% | 7.6% | 6.0% | 4.500 |
| nlptown text | 82.4% | 8.2% | 9.4% | 4.398 |
| Gap (model − human rating) | −4.0 pp | +0.6 pp | +3.4 pp | −0.102 |

The text supports the 4.5. Sixteen reviews are strict false negatives (human 4–5, model 1–2). The examples, the phrase pattern, and the manual read of 18 reviews are in the notebook conclusions.

## Run

Verified with Python 3.12. `torch` is the CPU wheel.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/app.py
pytest
```

`python src/app.py` reads `data/raw/reviews.csv` and writes `data/processed/reviews_with_sentiment.csv`. The first run downloads the model. Weights are not in git.

Re-execute the notebook from the repository root:

```bash
python -m nbconvert --to notebook --execute --inplace src/explore.ipynb
```

## Layout

| Path | Role |
| --- | --- |
| `data/raw/reviews.csv` | Official 500 reviews |
| `data/processed/reviews_with_sentiment.csv` | Stars, band, score, false-negative flag |
| `src/explore.ipynb` | Objectives through conclusions |
| `src/app.py` | Production inference |
| `src/utils.py` | Template database helper. This analysis does not call it |
| `tests/test_app.py` | Bands, single load, CSV contract, one real-model smoke test |
| `PROVENANCE.md` | Template commit and dataset hash |

## Model

- `nlptown/bert-base-multilingual-uncased-sentiment`
- Revision `8f6f4e3a8f70be4b65d3a4a8762b6d781cda240d`
- Loaded once with `pipeline("sentiment-analysis", revision=...)`
- Bands: 1–2 Negative, 3 Neutral, 4–5 Positive

The model was fine-tuned on product reviews. These rows are service reviews. That mismatch is part of the notebook, not a reason to swap the model.

## Provenance

Imported from [machine-learning-python-template](https://github.com/4GeeksAcademy/machine-learning-python-template) at `b49eff6673b76ba5b0003103e32f62a2eb9904a4`. That commit has no `LICENSE` file, and none was added here. Dataset sha256 and the model revision are in `PROVENANCE.md`.

There is no user interface in this project.
