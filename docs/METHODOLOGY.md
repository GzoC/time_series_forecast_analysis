# Diseño de la evaluación

Objetivo: energía diaria (kWh), horizonte 1–7 días. Agregación por fecha declarada, no por turno de producción. Una única planta y un año no acreditan generalización.

Los parámetros y cortes están fijados en código antes de seleccionar. Entrenamiento creciente; orígenes expresados como número de días disponibles:

| Fase | Orígenes | Uso |
|---|---|---|
| Validación |196,210,224,238|Elegir menor MAE de 28 predicciones|
| Calibración |252,266,280,294|Errores absolutos del modelo elegido|
| Prueba |308,322,336,350|Comparación final y cobertura sin volver a elegir|

Cada origen pronostica los siete días siguientes. Las fechas objetivo de las tres fases son disjuntas y ordenadas. Cortes posteriores pueden incorporar observaciones de cortes anteriores, ya disponibles en ese momento: simula reajuste periódico. El modelo se reentrena finalmente con todo el historial para la semana posterior al cierre; esa semana carece de observaciones reales en este estudio.

Candidatos: semana anterior; media por día de semana en últimos 56 días; SARIMA(1,0,0)(1,0,0,7) con constante; Prophet con estacionalidad semanal, sin anual/diaria ni covariables contemporáneas. Parámetros fijos, sin búsqueda sobre prueba. Todos los pronósticos se limitan a energía no negativa. Se registran advertencias de ajuste.

No hay limpieza aprendida ni escalador: se preservan valores medidos y se rechazan datos inválidos. Se exige continuidad diaria. No se imputan faltantes con observaciones posteriores ni se eliminan picos de consumo. Las métricas exigen igualdad exacta de índices antes de restar, corrigiendo el fallo anterior de alineación. WAPE es nulo cuando el denominador total es cero; MAE y RMSE siguen definidos.

Bandas: cuantil de errores absolutos agrupados de 28 predicciones de calibración; rango ceil((n+1)*0,9), limitado a n. Radio fijo por día, límite inferior truncado en cero. Es una adaptación práctica basada en residuos pasados; la dependencia temporal impide atribuir garantía conformal de 90%. Se reportan cobertura y ancho empíricos. Son bandas marginales diarias, no una probabilidad conjunta semanal. Cuatro observaciones por horizonte dan evidencia limitada.

La demo compara el límite superior diario con un presupuesto ingresado para señalar días a revisar. No optimiza producción, calcula tarifas ni controla equipos. Para uso operativo harían falta más años/plantas, calendario de producción disponible antes del corte, tratamiento acordado de indisponibilidad de sensores, tarifas y validación prospectiva. Se requiere revisar la anchura de las bandas y los fallos, no solo cobertura.
