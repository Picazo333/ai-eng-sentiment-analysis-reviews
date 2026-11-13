"""Tests for the production inference path.

Unit tests inject a fake pipeline so they do not download weights.
`test_real_model_smoke` loads the pinned public model once.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd
import pytest

import app

ROOT = Path(__file__).resolve().parents[1]


def _reviews(rows: list[tuple[int, int, str]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["review_id", "rating", "review_text"])


def _pipe_from_labels(labels: list[str]):
    def pipe(texts, **kwargs):
        assert kwargs.get("batch_size") == 32
        assert kwargs.get("truncation") is True
        assert len(texts) == len(labels)
        return [{"label": label, "score": 0.91} for label in labels]

    return pipe


def test_star_parser_and_bands():
    assert app.predicted_stars("1 star") == 1
    assert app.predicted_stars("2 stars") == 2
    assert app.predicted_stars("5 stars") == 5
    assert app.sentiment_band(1) == "Negative"
    assert app.sentiment_band(2) == "Negative"
    assert app.sentiment_band(3) == "Neutral"
    assert app.sentiment_band(4) == "Positive"
    assert app.sentiment_band(5) == "Positive"
    with pytest.raises(ValueError):
        app.predicted_stars("positive")
    with pytest.raises(ValueError):
        app.sentiment_band(0)


def test_annotate_does_not_reload_and_flags_false_negatives():
    frame = _reviews(
        [
            (1, 5, "Warm staff and a perfect coffee."),
            (2, 4, "We waited, but I would come back."),
            (3, 3, "It was fine."),
            (4, 1, "Rude cashier and a long wait."),
        ]
    )
    annotated = app.annotate_reviews(
        frame,
        _pipe_from_labels(["5 stars", "1 star", "3 stars", "2 stars"]),
    )
    assert annotated["sentiment"].tolist() == [
        "Positive",
        "Negative",
        "Neutral",
        "Negative",
    ]
    assert annotated["predicted_stars"].tolist() == [5, 1, 3, 2]
    assert annotated["false_negative"].tolist() == [0, 1, 0, 0]
    assert (annotated["model_revision"] == app.MODEL_REVISION).all()
    assert (annotated["model_id"] == app.MODEL_ID).all()


def test_run_loads_the_model_once_and_writes_csv(tmp_path, monkeypatch):
    calls = {"n": 0}

    def fake_load():
        calls["n"] += 1
        return _pipe_from_labels(["4 stars", "3 stars"])

    monkeypatch.setattr(app, "load_sentiment_pipeline", fake_load)
    source = tmp_path / "reviews.csv"
    _reviews([(10, 5, "Good"), (11, 3, "Okay")]).to_csv(source, index=False)
    destination = tmp_path / "processed" / "reviews_with_sentiment.csv"

    annotated = app.run(source, destination)

    assert calls["n"] == 1
    assert destination.is_file()
    saved = pd.read_csv(destination)
    assert len(saved) == len(annotated) == 2
    assert saved["sentiment"].tolist() == ["Positive", "Neutral"]
    assert saved["review_text"].tolist() == ["Good", "Okay"]


def test_injected_pipeline_skips_the_loader(tmp_path, monkeypatch):
    def boom():
        raise AssertionError("the model loader must not run when a pipeline is injected")

    monkeypatch.setattr(app, "load_sentiment_pipeline", boom)
    source = tmp_path / "reviews.csv"
    _reviews([(1, 5, "Great service")]).to_csv(source, index=False)
    destination = tmp_path / "reviews_with_sentiment.csv"

    annotated = app.run(source, destination, pipe=_pipe_from_labels(["5 stars"]))

    assert destination.is_file()
    assert annotated.loc[0, "sentiment"] == "Positive"


def test_missing_column_and_empty_frame_fail():
    with pytest.raises(ValueError, match="Missing columns"):
        app.annotate_reviews(pd.DataFrame({"review_id": [1]}), _pipe_from_labels([]))
    with pytest.raises(ValueError, match="No reviews"):
        app.annotate_reviews(
            pd.DataFrame(columns=["review_id", "rating", "review_text"]),
            _pipe_from_labels([]),
        )


def test_loader_is_not_called_inside_a_loop():
    tree = ast.parse((ROOT / "src" / "app.py").read_text(encoding="utf-8"))
    forbidden = {"load_sentiment_pipeline", "pipeline", "from_pretrained"}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.For, ast.While)):
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            func = child.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            assert name not in forbidden


def test_model_pin_is_a_full_revision():
    assert app.MODEL_ID == "nlptown/bert-base-multilingual-uncased-sentiment"
    assert app.MODEL_REVISION != "main"
    assert len(app.MODEL_REVISION) == 40


def test_comparison_table_uses_the_same_bands():
    frame = _reviews([(1, 5, "a"), (2, 4, "b"), (3, 3, "c"), (4, 1, "d")])
    annotated = app.annotate_reviews(
        frame,
        _pipe_from_labels(["5 stars", "2 stars", "3 stars", "1 star"]),
    )
    table = app.comparison_against_rating(annotated).set_index("source")
    human = table.loc["Human rating (bands; mean is the stated 4.5)"]
    model = table.loc["nlptown text sentiment"]
    gap = table.loc["Gap (model − human rating)"]
    assert human["positive_pct"] == 50.0
    assert human["neutral_pct"] == 25.0
    assert human["negative_pct"] == 25.0
    assert human["mean_stars"] == 3.25
    assert model["positive_pct"] == 25.0
    assert model["negative_pct"] == 50.0
    assert gap["positive_pct"] == -25.0
    assert table.attrs["stated_average_rating"] == 4.5


def test_weights_are_gitignored_and_not_in_the_tree():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for token in ("*.safetensors", "*.bin", "*.h5", ".venv/"):
        assert token in ignore
    skipped = {".venv", ".git", ".cache", ".pytest_cache", ".ipynb_checkpoints"}
    offenders = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or skipped.intersection(path.parts):
            continue
        if path.suffix in {".safetensors", ".bin", ".h5", ".msgpack", ".pt", ".pth", ".onnx"}:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_official_processed_csv_contract():
    raw_path = ROOT / "data" / "raw" / "reviews.csv"
    processed_path = ROOT / "data" / "processed" / "reviews_with_sentiment.csv"
    raw = pd.read_csv(raw_path)
    processed = pd.read_csv(processed_path)
    assert len(raw) == len(processed) == 500
    merged = raw.merge(processed, on=["review_id", "rating", "review_text"], how="inner")
    assert len(merged) == 500
    assert processed["predicted_stars"].between(1, 5).all()
    assert set(processed["sentiment"].unique()) <= set(app.SENTIMENT_BANDS)
    expected = processed["predicted_stars"].map(app.sentiment_band)
    assert (expected == processed["sentiment"]).all()
    assert (processed["model_id"] == app.MODEL_ID).all()
    assert (processed["model_revision"] == app.MODEL_REVISION).all()
    false_negatives = (
        (processed["rating"] >= 4) & (processed["predicted_stars"] <= 2)
    ).astype(int)
    assert (false_negatives == processed["false_negative"]).all()
    assert processed["predicted_score"].between(0, 1).all()


@pytest.mark.real_model
def test_real_model_smoke_loads_once_and_orders_obvious_lines():
    pipe = app.load_sentiment_pipeline()
    frame = _reviews(
        [
            (1, 5, "Excellent product quality. I love it. Highly recommend."),
            (2, 1, "Worst purchase ever. It broke immediately. Terrible quality."),
        ]
    )
    annotated = app.annotate_reviews(frame, pipe)
    assert annotated.loc[0, "sentiment"] == "Positive"
    assert annotated.loc[1, "sentiment"] == "Negative"
    assert annotated.loc[0, "predicted_stars"] > annotated.loc[1, "predicted_stars"]
    assert set(annotated["model_revision"]) == {app.MODEL_REVISION}
