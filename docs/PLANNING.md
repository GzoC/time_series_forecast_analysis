# Planificación acotada de cargas flexibles

## Alcance y datos

Demostración independiente del pronóstico UCI. Cinco tareas genéricas de lavado, calentamiento, preparación de aire, terminación y secado, sin afirmar que representan esos procesos físicos en una planta determinada. Potencia constante y duración obligatoria son supuestos; no se modela calentamiento, presión, rampas, caudal, estanques ni arranques de motores. No se eligió un escenario de bombas/estanques que necesitaría balances de inventario adicionales.

Entradas de `Scenario`: `interval_hours` (h), `capacity_kw` (kW), `base_kw` (potencia base estimada por intervalo), `tariff_usd_per_kwh` (USD/kWh), tareas con `power_kw`, `duration_intervals`, `release`, `deadline` exclusivo, `required_kwh` y `fixed_start`. Los vectores se consideran disponibles antes de decidir, como una estimación sintética y una tarifa anunciada. No son mediciones futuras usadas con retrospectiva. Ventanas expresadas en índices de intervalo, no fechas observadas. Temperatura y ciclo de vida de los equipos están fuera de alcance.

Solo valores finitos y no negativos; intervalo/capacidad/potencia de tarea estrictamente positivos, duraciones/ventanas enteras y tareas únicas. No se admiten tarifas negativas en este modelo reducido. Un requerimiento energético mayor que potencia × duración × intervalo hace la tarea inviable; no se ajusta silenciosamente su duración.

## Formulación y unidades

Sea x[j,s] binaria: la tarea j comienza en s. Sus inicios permitidos cumplen release[j] ≤ s y s+duration[j] ≤ deadline[j]. Cada tarea obligatoria empieza exactamente una vez y funciona sin interrupción durante su duración.

- Σ_s x[j,s] = 1 para cada tarea.
- P[i] = B[i] + Σ_j p[j] × Σ_{s: s ≤ i < s+d[j]} x[j,s].
- P[i] ≤ capacidad en todos los intervalos.
- Energía entregada a j = p[j] (kW) × d[j] (intervalos) × Δt (h/intervalo) ≥ demanda requerida (kWh).
- Costo total = Σ_i P[i] (kW) × Δt (h) × tarifa[i] (USD/kWh).

El costo base se incluye en la comparación y es constante para un escenario. Desplazar tareas puede reducir costo sin reducir energía. Ejemplo comprobado por prueba: 1 kW durante dos intervalos de 0,25 h entrega 0,5 kWh; con USD 2/kWh cuesta USD 1. No se suman kW como si fueran kWh sin multiplicar por duración.

## Comparaciones y prueba de optimalidad

**Fija:** horarios declarados en la configuración, comprobados con las mismas restricciones. **Heurística:** recorre tareas en el orden de entrada, asigna el inicio de menor costo que cabe con las ya asignadas, desempata por inicio anterior. Puede bloquear tareas posteriores; fallar no prueba inviabilidad global.

**Optimización:** enumeración branch-and-bound, adecuada a cinco tareas y doce intervalos (12.544 combinaciones de inicios antes de aplicar capacidad). Ordena tareas por cantidad de opciones; cada nodo obtiene una cota inferior sumando los menores costos independientes de las tareas restantes. Ignorar la capacidad en esa cota solo puede abaratar, por lo que es admisible. Se poda cuando la cota no mejora al incumbente. La búsqueda completa demuestra optimalidad de este modelo discreto dentro de tolerancia USD 1e-9; no demuestra óptimo de una planta real ni soporta escala ilimitada.

Presupuesto predeterminado: 1.000.000 de nodos. Si se agota y existe incumbente, estado `feasible`, optimal=false. Sin incumbente: `unknown`, salida CLI 3. Solo la prueba completa sin solución produce `infeasible`, salida 2; el informe se guarda igualmente. Las pruebas contrastan el solucionador con una enumeración independiente en casos pequeños, no solo con sus propias funciones de validación.

## Sensibilidad y vínculo con pronóstico

Se estresa el horario nominal con factores de potencia base 0,9 / 1,0 / 1,1 / 1,2 y se informa si aún cumple capacidad. Por separado se reoptimiza suponiendo que el nuevo escenario se conoce antes de decidir. Tarifas de intervalos 4–7 varían por factores 0,75 / 1,25 / 1,5. Estos factores son supuestos explícitos, no cuantiles derivados del dataset ni observaciones futuras.

El escenario nominal entrega 206 kWh flexibles y 788 kWh totales. Los resultados y costos proceden de `energy-forecast plan`; no se introducen métricas a mano. El horario nominal incumple capacidad con +20% de carga base. Reoptimizar ese escenario no acredita que pueda conocerse de antemano ni garantiza robustez ante cualquier incertidumbre.

El pronóstico diario puede apoyar presupuestos diarios, pero no define una forma intradiaria ni una potencia máxima. Para enlazarlo al despacho se necesitaría un modelo de perfiles independiente, reglas de flexibilidad y disponibilidad de información verificadas antes del corte. La demo conserva ambos ejercicios separados; no asigna un perfil sintético a la planta UCI.

## Defensa en entrevista

«El valor está en separar predicción y decisión. Primero compruebo cuánto me equivoco fuera de muestra. Después, en un escenario sintético independiente, transformo demanda y tarifa en un horario factible. Ahorro tarifario simulado no equivale a ahorro industrial ni a menor energía».

«No reeligí Prophet porque ganara en prueba. La media por día se eligió previamente en validación. Calibración y prueba son posteriores y disjuntas. Las bandas amplias y una muestra de 28 puntos impiden prometer cobertura futura».

«La heurística entrega rápido un horario pero puede desperdiciar capacidad barata. La búsqueda pequeña tiene una cota válida y un criterio explícito de terminación; digo óptima solo con prueba completa. Si falta capacidad, informo inviabilidad en vez de omitir tareas. Mi prueba de 15 minutos evita confundir potencia con energía».

«La sensibilidad enseña cuándo un horario deja de servir. No uso el consumo real futuro para decidir: cambio supuestos de entrada y distingo ese análisis de una decisión operativa real. No hay conexión ni escritura hacia equipos».
