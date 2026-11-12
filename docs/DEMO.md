# Demo de 2–3 minutos

Preparación:

```bash
uv sync --locked --extra dev
uv run --no-sync energy-forecast run
uv run --no-sync energy-forecast plan
uv run --no-sync energy-forecast dashboard
```

1. **0:00–0:40:** Pronóstico diario (UCI) → Evaluación. Explica validación, calibración y prueba separadas. Muestra la comparación y por qué no se reelige retrospectivamente otro modelo. Declara que la serie termina en 2018.
2. **0:40–1:20:** Despacho sintético. Muestra costos fija/heurística/óptima, energía flexible idéntica, Gantt, ventanas y curva de potencia frente a capacidad. Todo el escenario es sintético y separado de UCI.
3. **1:20–1:50:** cambia capacidad a 45 kW. Aparece inviabilidad: la propia carga base supera capacidad. No se presenta un horario incompleto como válido. Vuelve a 85 kW.
4. **1:50–2:20:** muestra sensibilidad +20% de carga base y el riesgo del horario nominal. Distingue estrés de un horario fijo y reoptimización con nuevos supuestos. Descarga CSV del despacho y configuración.
5. **2:20–2:50:** explica límites: tarifas anunciadas supuestas, potencia constante, sin inventarios/dinámica física ni ahorro industrial acreditado. La planificación sigue funcionando sin informes de pronóstico; los comandos son independientes.

[Defensa técnica y formulación](PLANNING.md). Capturas reales: planning-optimal, planning-schedule, planning-infeasible, planning-sensitivity, planning-mobile, planning-without-forecast y forecast-evaluation. browser.json registra versión y flujo observado; la descarga CSV se cotejó con los resultados numéricos del optimizador.
