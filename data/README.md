# Procedencia de los datos

Fuente: [Steel Industry Energy Consumption / UCI851](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption). V E, S., Shin, C., & Cho, Y. (2021). DOI10.24432/C52G8C. Licencia [CC BY4.0](https://creativecommons.org/licenses/by/4.0/). UCI atribuye los registros a DAEWOO Steel Co. Ltd, Gwangyang, Corea del Sur.

Descarga: https://archive.ics.uci.edu/static/public/851/steel+industry+energy+consumption.zip. Archivo original `raw/Steel_industry_data.csv`, sin modificar bytes ni finales de línea. SHA256: `9b1cee6f9cb9cd9df2b95814ca90a9a2ff15b7f5f1fba0fae3c643e82072eacc`. Recuperado29/10/2026.

Transformación propia: se suman Usage_kWh por fecha declarada. Se comprueban 35.040 registros, fechas únicas y96 observaciones por día. Resultado365 días de2018. La fila00:00 aparece al final de cada bloque diario en el original; se conserva su fecha declarada sin inventar huso horario o convención de intervalo. Otra definición del día operativo requiere confirmación del proveedor.

No se utilizan Load_Type, CO2, potencias reactivas ni factores de potencia para anticipar energía: son mediciones/etiquetas contemporáneas cuya disponibilidad futura no se ha demostrado. Se preservan picos y ceros; valores ausentes o negativos producen error explícito. No se interpolan huecos ni se ajustan umbrales con toda la serie.
