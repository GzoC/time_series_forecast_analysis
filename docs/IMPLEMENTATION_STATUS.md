# Entrega de planificación · 12 noviembre 2026

Base `6167731f2cc312d6f49b98ffe876dc966069c942`, rama `codex/constrained-load-planning`. PR #1 ya está integrado en esta base; el registro histórico inferior se conserva como evidencia de aquella entrega. Sin cambios locales iniciales. Se conservaron dataset, hash, modelos, cortes, lock y la evaluación cronológica existente.

| Requisito | Estado y evidencia |
|---|---|
| 1 evaluación cronológica | Existente y comprobada de nuevo; test_forecast; evaluación completa |
| 2 referencias sin reelección en prueba | Conservado; weekday_mean sigue seleccionado en validación |
| 3 métricas físicas y bandas | Regeneradas por CLI; reports/metrics y RESULTS; sin garantía de cobertura |
| 4 escenario sintético separado | Implementado; Scenario/Task, scenario.json, ejecución sin archivos de pronóstico |
| 5 fija/heurística/optimización | Implementado y comprobado contra oráculo independiente |
| 6 capacidad y cumplimiento | Implementado; ventanas, continuidad, demanda mínima, casos inviables y duración de intervalo |
| 7 sensibilidad | Implementado; carga base y tarifa, estrés nominal y reoptimización separados |
| 8 vista de programación | Implementada e inspeccionada en Chromium; Gantt, costo, capacidad, sensibilidad y CSV |

Baseline: 15 pruebas aprobadas. Final: 34 pruebas en Python 3.12.14; Ruff; evaluación real; planificación; wheel/sdist. Modelo seleccionado MAE 602,04 kWh/día, referencia semanal 860,48; cobertura observada 100% de 28 puntos con banda amplia. Prophet/SARIMA cambian levemente por entorno numérico respecto a Windows; no se modificaron objetivos, cortes ni estrategia de selección.

Planificación nominal generada: 206 kWh flexibles en todos los métodos; costos USD 132,62 / 122,48 / 120,08. Solo resultado simulado. Con presupuesto de un nodo, se entrega incumbente factible sin afirmar optimalidad. Con capacidad insuficiente, informe y salida 2, sin despacho válido.

Revisión visual real: escritorio y móvil; programación nominal, Gantt y capacidad, caso inviable 45 kW, sensibilidad de carga base 1,2, descarga CSV cotejada, evaluación histórica conservada y planificación con FORECAST_REPORTS apuntando a una carpeta inexistente. Evidencia en docs/evidence/browser.json y capturas asociadas. Ningún contenedor de este repositorio se ejecutó localmente en esta ampliación; CI conserva build/salud Docker y añade planificación. No hay despliegue público ni escritura OT.

[Formulación, supuestos y defensa en español](PLANNING.md) · [Demo](DEMO.md). READMEs inglés/español enlazados.

## Registro histórico preservado

# Estado — 29 de octubre de 2026

Implementación y validación terminadas en `codex/industrial-energy-forecast`. [PR #1](https://github.com/GzoC/time_series_forecast_analysis/pull/1): integración en `main` pendiente de autorización específica. Historia anterior conservada en Git y bundle.

## Evidencia ejecutada

- Local Windows, Python 3.12.13: 15 pruebas, Ruff y evaluación completa aprobados. NumPy 2.4.6 fijado por lock; el informe registra cero advertencias de ajuste.
- GitHub Actions [40878579250](https://github.com/GzoC/time_series_forecast_analysis/actions/runs/40878579250), commit de implementación `80ec27701b1c8f87d6ae870c7d570ae451ccf670`: Python 3.11/3.13, pruebas, estudio, construcción de paquetes y ejecución del wheel fuera del checkout aprobados.
- El mismo run construyó la imagen Docker y verificó salud HTTP de su dashboard. Docker no fue ejecutado localmente; el health check no constituye una prueba visual del contenedor.
- Navegador integrado sobre la aplicación local: escritorio 1280×900 y móvil 390×844, sin desbordamiento horizontal de página. Gráfico y controles visibles.
- Presupuestos 0, 4.000 y 10.000 kWh producen respectivamente 7, 6 y 0 días a revisar.
- Descarga real energy-plan.csv cotejada mediante pandas con reports/forecast.csv: siete filas, cuatro columnas y mismos valores/fechas.
- Cambio de corte desde 4 de noviembre a 16 de diciembre actualiza el gráfico a 17–23 de diciembre. Pestaña de datos muestra los 365 días y procedencia.
- La primera revisión detectó dos avisos Vega de extensión infinita del gráfico histórico. Se reemplazó st.line_chart por especificación Altair explícita; después de recargar, visitar la fuente y volver al plan no aparecieron avisos nuevos ni errores. El registro conserva los dos avisos históricos, no se presenta como consola vacía.

Capturas: [escritorio](images/forecast-desktop.png), [móvil](images/forecast-mobile.png), [controles móviles](images/forecast-mobile-chart.png), [serie original](images/forecast-source-mobile.png). Son vistas de la aplicación, no una validación con una planta real.

## Resultado y alcance

Media por día de semana seleccionada en validación. MAE de prueba 602,04 kWh/día frente a 860,48 del baseline semanal. Prophet obtiene 497,17 en prueba; no se reelige retrospectivamente. Bandas amplias: radio 2.877,95 kWh y cobertura observada 100% sobre 28 puntos. No garantizan cobertura futura, ahorro económico ni transferencia a otras plantas.

La CI del último commit de implementación se verificó completa y aprobada. Los checks del PR registran también las ejecuciones posteriores de documentación. Solo queda autorización para integrar y, después, comprobar la CI de `main`. No hay despliegue público ni Docker local comprobado.
