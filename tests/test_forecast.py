from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from energy_forecast.data import load_source, validate_daily
from energy_forecast.evaluation import ORIGINS, backtest, interval_radius, metrics
from energy_forecast.models import MODELS, predict

DATA = Path(__file__).parents[1] / "data/raw/Steel_industry_data.csv"


def test_source_daily_coverage_and_total():
    raw = pd.read_csv(DATA)
    series = load_source(DATA)
    assert len(series) == 365
    assert str(series.index[0].date()) == "2018-01-01"
    assert str(series.index[-1].date()) == "2018-12-31"
    assert series.sum() == pytest.approx(raw.Usage_kWh.sum())


def test_alignment_regression_and_zero_energy():
    dates = pd.date_range("2020-01-01", periods=2)
    actual = pd.Series([0.0, 0.0], index=dates)
    predicted = pd.Series([1.0, 2.0], index=dates)
    result = metrics(actual, predicted)
    assert result["mae_kwh"] == 1.5 and result["wape_percent"] is None
    with pytest.raises(ValueError, match="fechas"):
        metrics(actual, predicted.reset_index(drop=True))
    with pytest.raises(ValueError, match="fechas"):
        metrics(actual, predicted.iloc[::-1])


@pytest.mark.parametrize("kind", ["missing_day", "duplicate", "nan", "negative", "unsorted"])
def test_quality_failure_never_interpolates(kind):
    x = pd.Series(np.arange(60, dtype=float), index=pd.date_range("2020-01-01", periods=60))
    if kind == "missing_day":
        x = x.drop(x.index[3])
    if kind == "duplicate":
        x = pd.concat([x, x.iloc[-1:]])
    if kind == "nan":
        x.iloc[2] = np.nan
    if kind == "negative":
        x.iloc[2] = -1
    if kind == "unsorted":
        x = x.iloc[::-1]
    with pytest.raises(ValueError):
        validate_daily(x)


def test_future_changes_cannot_change_cutoff_prediction():
    x = load_source(DATA)
    changed = x.copy()
    changed.iloc[196:] = 1000000
    original_inputs = []

    def spy(history, model, horizon):
        original_inputs.append(history.copy())
        return predict(history, model, horizon)

    first, _ = backtest(x, [196], ["weekday_mean"], spy)
    second, _ = backtest(changed, [196], ["weekday_mean"], spy)
    pd.testing.assert_series_equal(original_inputs[0], original_inputs[1])
    np.testing.assert_array_equal(first.predicted, second.predicted)
    assert (first.date > first.origin).all()
    assert not first.actual.equals(second.actual)


def test_phase_targets_are_disjoint_and_ordered():
    sets = [
        {i for origin in origins for i in range(origin, origin + 7)} for origins in ORIGINS.values()
    ]
    assert max(sets[0]) < min(sets[1]) and max(sets[1]) < min(sets[2])
    assert all(len(s) == 28 for s in sets)


def test_seasonal_reference_repeats_last_week():
    x = load_source(DATA).iloc[:100]
    result, _ = predict(x, "seasonal_naive")
    np.testing.assert_array_equal(result.to_numpy(), x.iloc[-7:].to_numpy())


@pytest.mark.parametrize("model", MODELS)
def test_models_return_exact_future_dates(model):
    history = load_source(DATA).iloc[:100]
    result, notes = predict(history, model)
    assert result.index.equals(pd.date_range(history.index[-1] + pd.Timedelta(days=1), periods=7))
    assert np.isfinite(result).all() and (result >= 0).all()
    assert isinstance(notes, list)


def test_calibration_quantile_uses_finite_sample_rank():
    assert interval_radius(np.arange(1, 29)) == 27
    with pytest.raises(ValueError):
        interval_radius([np.nan])
