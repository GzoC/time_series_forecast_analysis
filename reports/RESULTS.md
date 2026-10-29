# Evaluación reproducible

Seleccionado en validación: **weekday_mean**. Horizonte: siete días.

| Modelo | MAE validación (kWh) | MAE prueba (kWh) | WAPE prueba (%) |
|---|---:|---:|---:|
| seasonal_naive | 917.14 | 860.48 | 37.26 |
| weekday_mean | 766.87 | 602.04 | 26.07 |
| sarima | 906.29 | 883.47 | 38.26 |
| prophet | 778.25 | 497.17 | 21.53 |

Cobertura observada de bandas nominales 90%: 100.0% en 28 predicciones reservadas. Radio 2877.95kWh. No garantiza cobertura futura ni semanal simultánea.

Los cortes, métricas por horizonte, versiones y advertencias están en metrics.json. No se corrigen picos ni se interpola el test. Una planta/un año no demuestra transferencia ni ahorro económico.
