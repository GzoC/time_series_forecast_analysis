import json
import os
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


def chart(frame, with_actual=True):
    base = alt.Chart(frame).encode(x=alt.X("date:T", title="Fecha"))
    band = base.mark_area(opacity=0.18, color="#127c78").encode(
        y=alt.Y("lower:Q", title="Energía diaria (kWh)"), y2="upper:Q"
    )
    forecast = base.mark_line(color="#127c78", point=True).encode(
        y="predicted:Q",
        tooltip=[
            "date:T",
            alt.Tooltip("predicted:Q", format=".0f"),
            alt.Tooltip("lower:Q", format=".0f"),
            alt.Tooltip("upper:Q", format=".0f"),
        ],
    )
    plot = band + forecast
    if with_actual:
        plot += base.mark_line(color="#354968", point=True).encode(
            y="actual:Q", tooltip=["date:T", alt.Tooltip("actual:Q", format=".0f")]
        )
    st.altair_chart(plot.properties(height=290), width="stretch")


def render():
    st.set_page_config(page_title="Energía industrial · Pronóstico", page_icon="⚡", layout="wide")
    st.caption("PLANIFICACIÓN INDUSTRIAL · SERIE DIARIA · HORIZONTE 7 DÍAS")
    st.title("Anticipar consumo, medir el margen")
    folder = Path(os.environ.get("FORECAST_REPORTS", "reports"))
    try:
        report = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
        future = pd.read_csv(folder / "forecast.csv", parse_dates=["date"])
        test = pd.read_csv(folder / "selected_test.csv", parse_dates=["date"])
        daily = pd.read_csv(folder / "daily.csv", parse_dates=["date"])
    except (OSError, ValueError):
        st.error(
            "Informe no disponible. Ejecuta energy-forecast run y vuelve a abrir la aplicación."
        )
        return
    st.info(
        f"Estudio histórico UCI: datos hasta {report['dataset']['last']}. La semana mostrada sigue a ese cierre; no es una predicción del consumo actual de una planta."
    )
    planning, evaluation, source = st.tabs(["Plan semanal", "Evaluación", "Datos y límites"])
    with planning:
        a, b, c = st.columns(3)
        a.metric("Energía prevista · 7 días", f"{future.predicted.sum():,.0f} kWh")
        b.metric("Modelo seleccionado", report["selected"])
        c.metric("MAE en prueba", f"{report['test'][report['selected']]['mae_kwh']:,.0f} kWh/día")
        chart(future, False)
        st.caption(
            "Verde: pronóstico. Banda: errores históricos de calibración, nominal90%. No garantiza cobertura futura ni cobertura simultánea de toda la semana."
        )
        budget = st.number_input(
            "Presupuesto diario de energía (kWh)", min_value=0.0, value=4000.0, step=250.0
        )
        risk = future[future.upper > budget]
        st.write(
            f"{len(risk)} de7 días tienen un límite superior mayor que el presupuesto indicado."
        )
        st.caption(
            "Úsalo como señal para revisar programación de producción y disponibilidad energética. No estima potencia máxima, tarifa, ahorro ni una orden automática de operación."
        )
        st.dataframe(future.round(1), hide_index=True, width="stretch")
        st.download_button(
            "Descargar plan semanal",
            future.to_csv(index=False).encode(),
            "energy-plan.csv",
            "text/csv",
        )
    with evaluation:
        st.subheader("Comparación en fechas reservadas")
        scores = pd.DataFrame(report["test"]).T.rename_axis("Modelo").reset_index()
        st.dataframe(scores.round(2), hide_index=True, width="stretch")
        st.caption(
            "El modelo se elige con MAE de validación, antes de calibrar bandas y evaluar prueba. WAPE omite división indefinida cuando toda la energía real es cero; MAE/RMSE permanecen definidos."
        )
        origin = st.selectbox("Cierre del entrenamiento", test.origin.unique())
        chart(test[test.origin == origin])
        st.caption(
            "Azul: energía observada. Verde: pronóstico del modelo elegido. Cada corte usa exclusivamente días anteriores a su pronóstico."
        )
        st.metric("Cobertura observada de la banda", f"{report['interval']['test_coverage']:.1%}")
        horizons = pd.DataFrame(
            [
                {"Día": int(h), **models[report["selected"]]}
                for h, models in report["by_horizon"].items()
            ]
        )
        st.dataframe(horizons.round(2), hide_index=True, width="stretch")
        st.caption(
            "Cuatro semanas de prueba; cada horizonte reúne solo cuatro observaciones. La muestra es pequeña y procede de una sola planta/año."
        )
        if report["warnings"]:
            with st.expander("Diagnósticos de ajuste"):
                st.dataframe(pd.DataFrame(report["warnings"]), hide_index=True)
    with source:
        st.subheader("Consumo agregado por fecha declarada")
        st.line_chart(daily.set_index("date")["kwh"], y_label="kWh/día", height=250)
        st.write(
            "35.040 registros originales, 96 por día. Solo fecha y Usage_kWh entran al estudio: no se usan mediciones eléctricas contemporáneas ni Load_Type como predictores futuros."
        )
        st.write(
            "La fuente coloca 00:00 al final del bloque de cada fecha. Se suma por esa fecha declarada, sin inventar un cambio horario. Una convención de cierre de turno distinta requiere validación con el proveedor."
        )
        st.write(
            "Se conservan picos y ceros. No se imputan faltantes, no se aprende limpieza sobre el futuro ni se recortan valores atípicos antes de dividir."
        )
        st.markdown(
            "[Fuente UCI y licencia CC BY4.0](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption) · DOI10.24432/C52G8C · V E, Shin y Cho (2021)."
        )


if __name__ == "__main__":
    render()
