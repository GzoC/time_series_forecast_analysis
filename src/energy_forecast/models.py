import warnings

import numpy as np
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .data import validate_daily

MODELS = ["seasonal_naive", "weekday_mean", "sarima", "prophet"]


def predict(history, model, horizon=7):
    history = validate_daily(history)
    if len(history) < 56 or horizon < 1 or horizon > 7:
        raise ValueError("Se necesitan 56 días y horizonte entre 1 y 7")
    dates = pd.date_range(history.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
    diagnostics = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        if model == "seasonal_naive":
            values = history.iloc[-7:].to_numpy()[:horizon]
        elif model == "weekday_mean":
            recent = history.iloc[-56:]
            means = recent.groupby(recent.index.dayofweek).mean()
            values = means.loc[dates.dayofweek].to_numpy()
        elif model == "sarima":
            fitted = SARIMAX(history, order=(1, 0, 0), seasonal_order=(1, 0, 0, 7), trend="c").fit(
                disp=False, maxiter=200
            )
            if not fitted.mle_retvals.get("converged", False):
                diagnostics.append("SARIMA optimizer did not converge")
            values = fitted.forecast(horizon).to_numpy()
        elif model == "prophet":
            frame = pd.DataFrame({"ds": history.index, "y": history.to_numpy()})
            fitted = Prophet(
                weekly_seasonality=True,
                yearly_seasonality=False,
                daily_seasonality=False,
                uncertainty_samples=0,
            )
            fitted.fit(frame, seed=42)
            values = fitted.predict(pd.DataFrame({"ds": dates}))["yhat"].to_numpy()
        else:
            raise ValueError("Modelo desconocido")
        diagnostics.extend(str(w.message) for w in caught)
    if not np.isfinite(values).all():
        raise ValueError("Pronóstico no finito")
    return pd.Series(np.maximum(values, 0), index=dates, name="predicted"), diagnostics
