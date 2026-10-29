import json
import math
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd

from .data import SOURCE_SHA, load_source
from .models import MODELS, predict

# Cutoffs are counts of available days, fixed before inspecting test outcomes.
ORIGINS = {
    "validation": [196, 210, 224, 238],
    "calibration": [252, 266, 280, 294],
    "test": [308, 322, 336, 350],
}


def metrics(actual, predicted):
    if not actual.index.equals(predicted.index) or len(actual) == 0:
        raise ValueError("Las métricas requieren las mismas fechas y orden")
    a, p = actual.to_numpy(dtype=float), predicted.to_numpy(dtype=float)
    if not np.isfinite(a).all() or not np.isfinite(p).all():
        raise ValueError("Métricas requieren valores finitos")
    error = a - p
    total = float(np.abs(a).sum())
    return {
        "mae_kwh": float(np.abs(error).mean()),
        "rmse_kwh": float(np.sqrt(np.mean(error**2))),
        "wape_percent": float(100 * np.abs(error).sum() / total) if total else None,
    }


def backtest(series, origins, models=MODELS, predictor=predict):
    rows, warnings = [], []
    for origin in origins:
        if origin < 56 or origin + 7 > len(series):
            raise ValueError("Corte fuera de cobertura")
        history, actual = series.iloc[:origin], series.iloc[origin : origin + 7]
        for model in models:
            forecast, notes = predictor(history, model, 7)
            metrics(actual, forecast)  # Fail if a model changes target dates.
            warnings.extend(
                {"model": model, "origin": str(history.index[-1].date()), "message": n}
                for n in notes
            )
            for h, (date, y, yhat) in enumerate(
                zip(actual.index, actual, forecast, strict=True), start=1
            ):
                rows.append(
                    {
                        "model": model,
                        "origin": history.index[-1].date().isoformat(),
                        "date": date.date().isoformat(),
                        "horizon": h,
                        "actual": float(y),
                        "predicted": float(yhat),
                    }
                )
    return pd.DataFrame(rows), warnings


def summarize(frame):
    output = {}
    for model, part in frame.groupby("model"):
        indexed = part.set_index(["origin", "date"])
        output[model] = metrics(indexed.actual, indexed.predicted)
    return output


def interval_radius(errors, coverage=0.9):
    errors = np.asarray(errors, dtype=float)
    if not len(errors) or not np.isfinite(errors).all() or (errors < 0).any():
        raise ValueError("Residuos de calibración inválidos")
    rank = min(len(errors), math.ceil((len(errors) + 1) * coverage))
    return float(np.sort(errors)[rank - 1])


def run(data_path, output):
    series = load_source(data_path)
    validation, notes = backtest(series, ORIGINS["validation"])
    validation_scores = summarize(validation)
    chosen = min(MODELS, key=lambda model: validation_scores[model]["mae_kwh"])
    calibration, messages = backtest(series, ORIGINS["calibration"], [chosen])
    notes += messages
    radius = interval_radius(abs(calibration.actual - calibration.predicted))
    test, messages = backtest(series, ORIGINS["test"])
    notes += messages
    chosen_test = test[test.model == chosen].copy()
    chosen_test["lower"] = (chosen_test.predicted - radius).clip(lower=0)
    chosen_test["upper"] = chosen_test.predicted + radius
    future, messages = predict(series, chosen)
    notes += [{"model": chosen, "origin": "final", "message": n} for n in messages]
    result = pd.DataFrame(
        {
            "date": future.index,
            "predicted": future.values,
            "lower": np.maximum(0, future.values - radius),
            "upper": future.values + radius,
        }
    )
    report = {
        "dataset": {
            "doi": "10.24432/C52G8C",
            "sha256": SOURCE_SHA,
            "rows": 35040,
            "days": len(series),
            "first": str(series.index[0].date()),
            "last": str(series.index[-1].date()),
        },
        "environment": {
            "python": platform.python_version(),
            **{p: version(p) for p in ["numpy", "pandas", "statsmodels", "prophet"]},
        },
        "origins": ORIGINS,
        "horizon_days": 7,
        "selected": chosen,
        "selection": "Lowest validation MAE, four fixed expanding-window folds; no test selection",
        "validation": validation_scores,
        "test": summarize(test),
        "by_horizon": {str(h): summarize(part) for h, part in test.groupby("horizon")},
        "interval": {
            "nominal_coverage": 0.9,
            "calibration_rows": len(calibration),
            "radius_kwh": radius,
            "test_coverage": float(
                (
                    (chosen_test.actual >= chosen_test.lower)
                    & (chosen_test.actual <= chosen_test.upper)
                ).mean()
            ),
            "mean_width_kwh": float((chosen_test.upper - chosen_test.lower).mean()),
            "limitation": "Pooled absolute errors from earlier calibration folds; temporal dependence means no coverage guarantee. Marginal daily bands, not simultaneous weekly coverage.",
        },
        "warnings": notes,
    }
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    series.rename_axis("date").to_csv(output / "daily.csv")
    for name, frame in [
        ("validation", validation),
        ("calibration", calibration),
        ("test", test),
        ("selected_test", chosen_test),
        ("forecast", result),
    ]:
        frame.to_csv(output / f"{name}.csv", index=False)
    (output / "metrics.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Evaluación reproducible",
        "",
        f"Seleccionado en validación: **{chosen}**. Horizonte: siete días.",
        "",
        "| Modelo | MAE validación (kWh) | MAE prueba (kWh) | WAPE prueba (%) |",
        "|---|---:|---:|---:|",
    ]
    for model in MODELS:
        lines.append(
            f"| {model} | {validation_scores[model]['mae_kwh']:.2f} | {report['test'][model]['mae_kwh']:.2f} | {report['test'][model]['wape_percent']:.2f} |"
        )
    lines += [
        "",
        f"Cobertura observada de bandas nominales90%: {report['interval']['test_coverage']:.1%} en28 predicciones reservadas. Radio {radius:.2f}kWh. No garantiza cobertura futura ni semanal simultánea.",
        "",
        "Los cortes, métricas por horizonte, versiones y advertencias están en metrics.json. No se corrigen picos ni se interpola el test. Una planta/un año no demuestra transferencia ni ahorro económico.",
    ]
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
