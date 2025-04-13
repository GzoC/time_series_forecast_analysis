# tests/test_modeling.py

import os
from src.ingestion.load_data import load_raw_data
from src.preprocessing.clean_data import clean_sales_data
from src.modeling.arima_model import train_test_split, select_arima_order, train_arima

def test_arima_training():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'raw', 'datos_ventas.csv')

    df = clean_sales_data(load_raw_data(csv_path))
    df.set_index('fecha', inplace=True)
    train, _ = train_test_split(df)

    order = select_arima_order(train['ventas'])
    model = train_arima(train['ventas'], order)

    assert hasattr(model, 'forecast'), "El modelo ARIMA no tiene método forecast"
