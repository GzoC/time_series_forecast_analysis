# tests/test_ingestion.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.ingestion.load_data import load_raw_data


def test_load_raw_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'raw', 'datos_ventas.csv')
    
    df = load_raw_data(csv_path)
    
    assert not df.empty, "El DataFrame cargado está vacío"
    assert 'fecha' in df.columns, "Falta la columna 'fecha'"
    assert 'ventas' in df.columns, "Falta la columna 'ventas'"
    assert pd.api.types.is_datetime64_any_dtype(df['fecha']), "La columna 'fecha' no es datetime"
