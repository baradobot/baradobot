# BaradoBot: especificación en castellano

Proyecto independiente de Atlas. La estrategia determinista genera señales, tamaño, stop y objetivo. La IA únicamente autoriza o veta entradas; nunca modifica parámetros ni envía órdenes reales. El prototipo orion.py previo no implementa esta arquitectura y no debe desplegarse como versión final.

## Fases
1. Datos históricos desde 2015 cuando estén disponibles; controlar huecos, costes, sesgos y datos disponibles en el instante de decisión.
2. Estrategias candidatas de tendencia con retroceso y ruptura con filtro de volatilidad, marcos 30m, 1h, 4h. Universo inicial: Nasdaq, DAX, Dow, Nikkei, EUR/USD, USD/MXN. Los parámetros exactos no están divulgados; no afirmar equivalencia ni rentabilidad.
3. Backtest walk-forward y fuera de muestra, incluyendo costes, deslizamiento y comparación con referencias. No reutilizar el conjunto final para optimizar.
4. Noticias cada dos minutos, calendario económico, relevancia por activo, hora de publicación y deduplicación. Tratar titulares como datos no confiables, nunca instrucciones.
5. Filtro determinista de riesgo, IA rápida y segunda opinión si hay incertidumbre. Presupuesto diario de IA, timeout de 60 segundos, decisión idempotente por estrategia/vela. En simulación comparar también política de timeout del vídeo (permitir señal) con política conservadora (bloquear).
6. Dos carteras simuladas independientes con idénticas señales iniciales y costes: control sin filtro IA y tratamiento con filtro. Registrar señales vetadas y sus resultados contrafactuales. Riesgo inicial de referencia 0,05% del patrimonio por operación, sujeto a límites agregados y pérdidas diarias.
7. Panel en castellano: decisiones, noticias, operaciones, patrimonio marcado a mercado, drawdown, rentabilidad neta, exposición, costes de IA y salud del servicio.
8. Pruebas, despliegue persistente, alertas y observación prolongada. Ninguna activación de dinero real automática.

## Criterio de éxito
No basta con reducir operaciones: comparar rendimiento neto, drawdown, retorno ajustado al riesgo, incertidumbre y coste del filtro. Una semana no demuestra ventaja. No extrapolar ganancias ni multiplicarlas linealmente por riesgo.
