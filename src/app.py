"""Production sentiment inference for the WeLoveReviews reviews.

The notebook tells the story. This script loads one pinned Hugging Face
model, scores every review, and writes the processed CSV.
"""

from __future__ import annotations

import os

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import re
import time
from pathlib import Path

import pandas as pd
from transformers import pipeline

MODEL_ID = "nlptown/bert-base-multilingual-uncased-sentiment"
# Public Hub revision resolved on 2026-11-06. Do not float to "main".
MODEL_REVISION = "8f6f4e3a8f70be4b65d3a4a8762b6d781cda240d"
SENTIMENT_BANDS = ("Positive", "Neutral", "Negative")
REQUIRED_COLUMNS = ("review_id", "rating", "review_text")
STATED_AVERAGE_RATING = 4.5

_STAR_RE = re.compile(r"([1-5])")


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_input_path() -> Path:
    return project_root() / "data" / "raw" / "reviews.csv"


def default_output_path() -> Path:
    return project_root() / "data" / "processed" / "reviews_with_sentiment.csv"


def predicted_stars(label: str) -> int:
    """Map a model label such as '5 stars' or '1 star' to an integer 1–5."""
    match = _STAR_RE.search(str(label))
    if match is None:
        raise ValueError(f"Unexpected sentiment label: {label!r}")
    return int(match.group(1))


def sentiment_band(stars: int) -> str:
    """Map stars to the bands required by the brief."""
    stars = int(stars)
    if stars in (1, 2):
        return "Negative"
    if stars == 3:
        return "Neutral"
    if stars in (4, 5):
        return "Positive"
    raise ValueError(f"Stars out of range: {stars}")


def load_sentiment_pipeline(
    model_id: str = MODEL_ID,
    revision: str = MODEL_REVISION,
):
    """Load the classifier once. Callers must reuse the returned pipeline."""
    return pipeline(
        task="sentiment-analysis",
        model=model_id,
        revision=revision,
        truncation=True,
        device="cpu",
        dtype="float32",
        model_kwargs={"low_cpu_mem_usage": True},
    )


def _top_prediction(item) -> tuple[str, float]:
    if isinstance(item, list):
        if not item:
            raise ValueError("Pipeline returned an empty prediction")
        item = max(item, key=lambda row: float(row["score"]))
    if not isinstance(item, dict) or "label" not in item or "score" not in item:
        raise ValueError(f"Unexpected pipeline output: {item!r}")
    return str(item["label"]), float(item["score"])


def annotate_reviews(reviews: pd.DataFrame, pipe) -> pd.DataFrame:
    """Score every row with an already loaded pipeline.

    `pipe` is an argument so this function cannot reload the model.
    """
    missing = [column for column in REQUIRED_COLUMNS if column not in reviews.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if reviews.empty:
        raise ValueError("No reviews to score")

    texts = reviews["review_text"].astype(str).tolist()
    raw_predictions = pipe(texts, batch_size=32, truncation=True)
    if len(raw_predictions) != len(reviews):
        raise ValueError(
            f"Pipeline returned {len(raw_predictions)} rows for {len(reviews)} reviews"
        )

    labels: list[str] = []
    scores: list[float] = []
    for item in raw_predictions:
        label, score = _top_prediction(item)
        labels.append(label)
        scores.append(score)

    stars = [predicted_stars(label) for label in labels]
    annotated = reviews.copy()
    annotated["predicted_label"] = labels
    annotated["predicted_score"] = scores
    annotated["predicted_stars"] = stars
    annotated["sentiment"] = [sentiment_band(star) for star in stars]
    annotated["false_negative"] = (
        (annotated["rating"].astype(int) >= 4) & (annotated["predicted_stars"] <= 2)
    ).astype(int)
    annotated["model_id"] = MODEL_ID
    annotated["model_revision"] = MODEL_REVISION
    return annotated


def _band_percent(series: pd.Series, band: str) -> float:
    if len(series) == 0:
        return 0.0
    return round(100 * float((series == band).sum()) / len(series), 2)


def comparison_against_rating(annotated: pd.DataFrame) -> pd.DataFrame:
    """Positive / neutral / negative shares against the stated 4.5 average.

    The 4.5 figure is a mean, not a mix. The human row uses the same star
    bands as the model and its mean is the dataset average (4.5 on this file).
    The gap row is model minus human rating.
    """
    human_band = annotated["rating"].astype(int).map(sentiment_band)
    model_band = annotated["sentiment"]
    human_mean = round(float(annotated["rating"].astype(float).mean()), 4)
    model_mean = round(float(annotated["predicted_stars"].astype(float).mean()), 4)
    rows = [
        {
            "source": "Human rating (bands; mean is the stated 4.5)",
            "positive_pct": _band_percent(human_band, "Positive"),
            "neutral_pct": _band_percent(human_band, "Neutral"),
            "negative_pct": _band_percent(human_band, "Negative"),
            "mean_stars": human_mean,
        },
        {
            "source": "nlptown text sentiment",
            "positive_pct": _band_percent(model_band, "Positive"),
            "neutral_pct": _band_percent(model_band, "Neutral"),
            "negative_pct": _band_percent(model_band, "Negative"),
            "mean_stars": model_mean,
        },
    ]
    rows.append(
        {
            "source": "Gap (model − human rating)",
            "positive_pct": round(rows[1]["positive_pct"] - rows[0]["positive_pct"], 2),
            "neutral_pct": round(rows[1]["neutral_pct"] - rows[0]["neutral_pct"], 2),
            "negative_pct": round(rows[1]["negative_pct"] - rows[0]["negative_pct"], 2),
            "mean_stars": round(model_mean - human_mean, 4),
        }
    )
    table = pd.DataFrame(rows)
    table.attrs["stated_average_rating"] = STATED_AVERAGE_RATING
    return table


def run(input_path: Path, output_path: Path, pipe=None) -> pd.DataFrame:
    """Read reviews, load the model at most once, and write the processed CSV."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    reviews = pd.read_csv(input_path)
    if pipe is None:
        pipe = load_sentiment_pipeline()
    annotated = annotate_reviews(reviews, pipe)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    annotated.to_csv(output_path, index=False)
    return annotated


def _print_summary(annotated: pd.DataFrame, output_path: Path, elapsed_s: float) -> None:
    table = comparison_against_rating(annotated)
    false_negatives = int(annotated["false_negative"].sum())
    print(f"model_id={MODEL_ID}")
    print(f"model_revision={MODEL_REVISION}")
    print(f"rows={len(annotated)}")
    print(f"false_negatives={false_negatives}")
    print(f"output={output_path}")
    print(f"elapsed_s={elapsed_s:.2f}")
    print("comparison_vs_4_5")
    print(table.to_string(index=False))


def main() -> None:
    input_path = default_input_path()
    output_path = default_output_path()
    started = time.perf_counter()
    pipe = load_sentiment_pipeline()
    annotated = run(input_path, output_path, pipe=pipe)
    elapsed_s = time.perf_counter() - started
    _print_summary(annotated, output_path, elapsed_s)


if __name__ == "__main__":
    main()
