"""Synthetic scheduling UI, usable without any forecast report or historical dataset."""

import json
from dataclasses import asdict, replace

import altair as alt
import pandas as pd
import streamlit as st

from energy_forecast.planning import compare, default_scenario, sensitivity


@st.cache_data
def calculate(scenario):
    plans = compare(scenario)
    return plans, sensitivity(scenario, plans["optimized"])


METHODS = {"fixed": "Fija", "greedy": "Heurística", "optimized": "Optimización"}
STATUSES = {
    "optimal": "Óptima",
    "feasible": "Factible",
    "infeasible": "Inviable",
    "no_feasible_schedule_found": "Sin solución hallada",
    "unknown": "Sin resolver",
}


def render_planning():
    st.subheader("Programar cargas flexibles con restricciones")
    st.info(
        "Escenario 100 % sintético y separado del dataset UCI. Potencias, ventanas y tarifas son supuestos disponibles antes de decidir. No es un perfil horario observado de la planta histórica."
    )
    a, b, c = st.columns(3)
    capacity = a.number_input(
        "Capacidad disponible (kW)", min_value=1.0, max_value=200.0, value=85.0, step=5.0
    )
    base_factor = b.number_input(
        "Multiplicador de carga base supuesta", min_value=0.5, max_value=2.0, value=1.0, step=0.1
    )
    price_factor = c.number_input(
        "Multiplicador tarifa pico (intervalos 4–7)",
        min_value=0.1,
        max_value=3.0,
        value=1.0,
        step=0.25,
    )
    default = default_scenario()
    scenario = replace(
        default,
        capacity_kw=capacity,
        base_kw=tuple(p * base_factor for p in default.base_kw),
        tariff_usd_per_kwh=tuple(
            t * price_factor if 4 <= i <= 7 else t for i, t in enumerate(default.tariff_usd_per_kwh)
        ),
    )
    plans, stress = calculate(scenario)
    st.caption(
        f"Horizonte: {len(scenario.base_kw)} intervalos de {scenario.interval_hours:g} h. Tareas obligatorias, potencia fija y ejecución continua. Costo en USD = Σ potencia (kW) × intervalo (h) × tarifa (USD/kWh). No incluye impuestos ni cargos por demanda."
    )
    rows = [
        {
            "Método": METHODS[name],
            "Estado": STATUSES[p["status"]],
            "Factible": p["feasible"],
            "Costo total (USD)": p["total_cost_usd"],
            "Energía flexible (kWh)": p["flexible_energy_kwh"],
            "Pico (kW)": p["peak_kw"],
        }
        for name, p in plans.items()
    ]
    st.dataframe(pd.DataFrame(rows).round(2), hide_index=True, width="stretch")
    optimum = plans["optimized"]
    if not optimum["feasible"]:
        excess = [
            i for i, power in enumerate(scenario.base_kw) if power > scenario.capacity_kw + 1e-9
        ]
        if excess:
            st.error(
                f"Escenario inviable: la carga base por sí sola supera la capacidad en los intervalos {excess}. No queda capacidad para cumplir el servicio, incluso sin cargas flexibles."
            )
        elif optimum["proven_infeasible"]:
            st.error(
                "Escenario inviable: ninguna programación cumple todas las tareas, ventanas y límites de capacidad."
            )
        else:
            st.warning(
                "Búsqueda sin resolver: se agotó el presupuesto antes de encontrar una programación factible."
            )
    else:
        st.success(
            f"{STATUSES[optimum['status']]} · Todas las tareas y límites comprobados. "
            + (
                "Optimalidad comprobada para este modelo discreto."
                if optimum["optimal"]
                else "Optimalidad pendiente de demostrar."
            )
        )
        if plans["fixed"]["feasible"]:
            reduction = plans["fixed"]["total_cost_usd"] - optimum["total_cost_usd"]
            st.metric("Reducción estimada frente a fija · simulada", f"USD {reduction:.2f}")
            st.caption(
                "Resultado de este escenario bajo sus supuestos; no acredita ahorro industrial ni reducción de energía: las tareas entregan la misma energía."
            )
    selected = st.selectbox(
        "Programación a inspeccionar", list(plans), index=2, format_func=lambda name: METHODS[name]
    )
    plan = plans[selected]
    if plan["feasible"]:
        tasks = pd.DataFrame(
            [
                {
                    "Tarea": t.task_id,
                    "Inicio (h)": plan["starts"][t.task_id] * scenario.interval_hours,
                    "Fin (h)": (plan["starts"][t.task_id] + t.duration_intervals)
                    * scenario.interval_hours,
                    "Potencia (kW)": t.power_kw,
                    "Demanda requerida (kWh)": t.required_kwh,
                    "Ventana desde (h)": t.release * scenario.interval_hours,
                    "Límite de fin (h)": t.deadline * scenario.interval_hours,
                }
                for t in scenario.tasks
            ]
        )
        st.altair_chart(
            alt.Chart(tasks)
            .mark_bar(color="#127c78", cornerRadius=3)
            .encode(
                x=alt.X(
                    "Inicio (h):Q",
                    title="Tiempo sintético desde el inicio (h)",
                    scale=alt.Scale(domain=[0, len(scenario.base_kw) * scenario.interval_hours]),
                ),
                x2="Fin (h):Q",
                y=alt.Y("Tarea:N", sort=None),
                tooltip=list(tasks.columns),
            )
            .properties(height=210),
            width="stretch",
        )
        st.dataframe(tasks, hide_index=True, width="stretch")
        intervals = pd.DataFrame(
            {
                "Intervalo": range(len(scenario.base_kw)),
                "Base (kW)": scenario.base_kw,
                "Flexible (kW)": plan["flexible_kw"],
                "Total (kW)": plan["total_kw"],
                "Capacidad (kW)": [scenario.capacity_kw] * len(scenario.base_kw),
                "Tarifa (USD/kWh)": scenario.tariff_usd_per_kwh,
            }
        )
        intervals["Energía (kWh)"] = intervals["Total (kW)"] * scenario.interval_hours
        intervals["Costo (USD)"] = intervals["Energía (kWh)"] * intervals["Tarifa (USD/kWh)"]
        long = intervals.melt(
            id_vars="Intervalo",
            value_vars=["Total (kW)", "Capacidad (kW)"],
            var_name="Serie",
            value_name="Potencia",
        )
        st.altair_chart(
            alt.Chart(long)
            .mark_line(point=True)
            .encode(
                x=alt.X("Intervalo:O", title="Intervalo sintético"),
                y=alt.Y("Potencia:Q", title="Potencia (kW)", scale=alt.Scale(zero=True)),
                color="Serie:N",
                tooltip=["Intervalo:O", "Serie:N", "Potencia:Q"],
            )
            .properties(height=230),
            width="stretch",
        )
        st.dataframe(intervals.round(3), hide_index=True, width="stretch")
        st.download_button(
            "Descargar despacho simulado",
            intervals.to_csv(index=False).encode(),
            f"{selected}-synthetic-dispatch.csv",
            "text/csv",
        )
    else:
        st.warning(
            f"{METHODS[selected]}: {STATUSES[plan['status']]}. No hay un despacho válido para mostrar."
        )
        with st.expander("Detalle de restricciones"):
            st.text("\n".join(plan["errors"]))
    with st.expander("Sensibilidad y restricciones", expanded=True):
        st.write(
            "Se aplica la programación nominal a cargas base supuestas diferentes y se comprueba si aún cumple capacidad. Reoptimizar supone que el escenario se conoce antes de decidir; no utiliza mediciones futuras observadas."
        )
        st.dataframe(pd.DataFrame(stress), hide_index=True, width="stretch")
        st.caption(
            "Estos factores no se derivan de los intervalos diarios del pronóstico. Una banda de energía diaria no define una envolvente de potencia horaria."
        )
    with st.expander("Supuestos, método y configuración reproducible"):
        st.write(
            "Optimización discreta por branch-and-bound para cinco tareas pequeñas. Una cota de costo admisible descarta ramas. Solo se declara óptimo al terminar la búsqueda; un presupuesto de nodos agotado puede dejar una solución factible sin prueba de optimalidad. No incluye dinámica de bombas, estanques, rampas, degradación ni arranques de motores."
        )
        st.json(asdict(scenario), expanded=False)
        st.download_button(
            "Descargar escenario",
            json.dumps(asdict(scenario), indent=2),
            "scenario.json",
            "application/json",
        )
        st.code("energy-forecast plan --scenario scenario.json --output reports/custom-planning")
