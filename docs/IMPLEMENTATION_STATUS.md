# Estado — 29 de octubre de 2026

Implementación terminada en codex/industrial-energy-forecast; PR #1 pendiente de la CI del cierre y autorización específica para integrar. Historia anterior conservada en Git y bundle.

## Evidencia ejecutada

- Local Windows, Python 3.12.13: 15 pruebas, Ruff y evaluación completa aprobados. NumPy 2.4.6 fijado por lock; el informe registra cero advertencias de ajuste.
- GitHub Actions [40872781514](https://github.com/GzoC/time_series_forecast_analysis/actions/runs/40872781514), commit 226c3fe0: Python 3.11/3.13, pruebas, estudio, construcción de paquetes y ejecución del wheel fuera del checkout aprobados.
- El mismo run construyó la imagen Docker y verificó salud HTTP de su dashboard. Docker no fue ejecutado localmente; el health check no constituye una prueba visual del contenedor.
- Navegador integrado sobre la aplicación local: escritorio 1280×900 y móvil 390×844, sin desbordamiento horizontal de página. Gráfico y controles visibles.
- Presupuestos 0, 4.000 y 10.000 kWh producen respectivamente 7, 6 y 0 días a revisar.
- Descarga real energy-plan.csv cotejada mediante pandas con reports/forecast.csv: siete filas, cuatro columnas y mismos valores/fechas.
- Cambio de corte desde 4 de noviembre a 16 de diciembre actualiza el gráfico a 17–23 de diciembre. Pestaña de datos muestra los 365 días y procedencia.
- La primera revisión detectó dos avisos Vega de extensión infinita del gráfico histórico. Se reemplazó st.line_chart por especificación Altair explícita; después de recargar, visitar la fuente y volver al plan no aparecieron avisos nuevos ni errores. El registro conserva los dos avisos históricos, no se presenta como consola vacía.

Capturas: [escritorio](images/forecast-desktop.png), [móvil](images/forecast-mobile.png), [controles móviles](images/forecast-mobile-chart.png), [serie original](images/forecast-source-mobile.png). Son vistas de la aplicación, no una validación con una planta real.

## Resultado y alcance

Media por día de semana seleccionada en validación. MAE de prueba 602,04 kWh/día frente a 860,48 del baseline semanal. Prophet obtiene 497,17 en prueba; no se reelige retrospectivamente. Bandas amplias: radio 2.877,95 kWh y cobertura observada 100% sobre 28 puntos. No garantizan cobertura futura, ahorro económico ni transferencia a otras plantas.

Pendiente exclusivamente: comprobar CI del commit de cierre, poner PR listo y obtener autorización de integración. No repetir validaciones históricas cerradas. No hay despliegue público ni Docker local comprobado.
