import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

SOURCE_SHA = "9b1cee6f9cb9cd9df2b95814ca90a9a2ff15b7f5f1fba0fae3c643e82072eacc"


def validate_daily(series):
    if not isinstance(series, pd.Series) or not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Se requiere una serie con índice de fechas")
    if series.empty or series.index.has_duplicates or not series.index.is_monotonic_increasing:
        raise ValueError("Fechas vacías, duplicadas o desordenadas")
    if series.index.tz is not None or not series.index.equals(series.index.normalize()):
        raise ValueError("Usa fechas diarias sin zona horaria, tal como declara la fuente")
    if not series.index.equals(pd.date_range(series.index[0], periods=len(series), freq="D")):
        raise ValueError("Faltan días; no se interpolan observaciones desconocidas")
    if not pd.api.types.is_numeric_dtype(series.dtype) or pd.api.types.is_bool_dtype(series.dtype):
        raise ValueError("Energía debe ser numérica")
    if not np.isfinite(series.to_numpy(dtype=float)).all() or (series < 0).any():
        raise ValueError("Energía ausente, infinita o negativa")
    return series.astype(float).copy()


def load_source(path):
    path = Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("La fuente no coincide con el SHA256 documentado")
    raw = pd.read_csv(path, encoding="utf-8-sig")
    dates = pd.to_datetime(raw["date"], format="%d/%m/%Y %H:%M", errors="raise")
    if len(raw) != 35040 or dates.duplicated().any():
        raise ValueError("Cobertura o fechas duplicadas en la fuente")
    # Midnight is labelled with the same day at the end of each source block.
    # Aggregate by declared date; do not invent a timezone or shift the observation.
    energy = pd.Series(raw["Usage_kWh"].to_numpy(), index=dates)
    if not np.isfinite(energy).all() or (energy < 0).any():
        raise ValueError("Mediciones de energía inválidas")
    if not energy.resample("D").count().eq(96).all():
        raise ValueError("Cada día debe contener sus 96 mediciones")
    daily = validate_daily(energy.resample("D").sum())
    daily.name = "kwh"
    return daily
