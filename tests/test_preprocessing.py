# tests/test_preprocessing.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.load_data import load_raw_data
from src.preprocessing.clean_data import clean_sales_data

def test_clean_sales_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'raw', 'datos_ventas.csv')

    df = load_raw_data(csv_path)
    clean_df = clean_sales_data(df)

    assert clean_df.isnull().sum().sum() == 0, "Existen valores nulos después de limpiar"
    assert clean_df['ventas'].min() > 0, "Hay ventas <= 0 después de limpiar"
