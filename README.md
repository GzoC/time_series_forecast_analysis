# Análisis y Pronóstico de Series Temporales

Este proyecto realiza un análisis y pronóstico de series temporales utilizando modelos predictivos avanzados (ARIMA y Prophet). El objetivo principal es realizar predicciones precisas sobre datos históricos como ventas, demanda, visitas, etc.

## 📂 Estructura del Proyecto

```
analisis-pronostico-series-temporales/
├── data/
│   ├── raw/
│   │   └── datos_ventas.csv
│   └── processed/
│       ├── datos_ventas_limpios.csv
│       └── arima_predictions.csv
├── notebooks/
│   └── exploratory_analysis.ipynb
├── src/
│   ├── ingestion/
│   │   └── load_data.py
│   ├── preprocessing/
│   │   └── clean_data.py
│   ├── modeling/
│   │   ├── arima_model.py
│   │   ├── prophet_model.py
│   │   └── model_evaluation.py (pendiente)
│   ├── visualization/
│   │   └── dashboard.py (pendiente)
│   └── utils/
│       └── utils.py (pendiente)
├── tests/
│   ├── test_ingestion.py (pendiente)
│   ├── test_preprocessing.py (pendiente)
│   └── test_modeling.py (pendiente)
├── Dockerfile (pendiente)
├── docker-compose.yml (pendiente)
├── requirements.txt
├── setup.py (opcional)
├── .gitignore
├── README.md
└── .github/
    └── workflows/
        └── ci.yml (pendiente)
```

## 🚀 Instalación

1. **Clonar el repositorio:**

```bash
git clone https://github.com/tuusuario/analisis-pronostico-series-temporales.git
cd analisis-pronostico-series-temporales
```

2. **Crear y activar entorno virtual:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

## 🧑‍💻 Ejecución del Pipeline

### 1. **Ingestión de Datos**

```bash
python src/ingestion/load_data.py
```

### 2. **Limpieza y Transformación**

```bash
python src/preprocessing/clean_data.py
```

### 3. **Modelado Predictivo (ARIMA)**

```bash
python src/modeling/arima_model.py
```

## 📦 Resultados

Los resultados se guardan automáticamente en:

- Datos limpios: `data/processed/datos_ventas_limpios.csv`
- Predicciones ARIMA: `data/processed/arima_predictions.csv`

## 📌 Próximos Pasos

- [ ] Desarrollar el modelo Prophet
- [ ] Evaluación comparativa de modelos
- [ ] Automatización del pipeline
- [ ] Dashboard interactivo (Streamlit)
- [ ] Contenerización (Docker)
- [ ] Testing (Pytest)
- [ ] CI/CD (GitHub Actions)

## 🛠️ Herramientas y Tecnologías

- Python
- Pandas, NumPy
- Statsmodels (ARIMA)
- Prophet (pendiente)
- Docker, Docker Compose (pendiente)
- Pytest, GitHub Actions (pendiente)

## 📞 Contacto

- **Email:** cisternasalinasg@gmail.com
- **GitHub:** [GzoC](https://github.com/GzoC)
