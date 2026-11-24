# BaradoBot / ORION AI
Agente independiente de Atlas. Solo paper trading; capital simulado 10.000 USD, BTC/ETH/SOL, velas Kraken de cinco minutos, decisiones LLM y SQLite. No envía órdenes reales. No se ha demostrado rentabilidad.

## Arranque
Copiar `.env.example` a `.env`, configurar una clave de API OpenAI (costes independientes de ChatGPT Plus), ejecutar `docker compose up -d --build`. Consultar `docker compose logs -f`; detener con `docker compose down`. Requiere servidor encendido y acceso a ambas APIs.

Pruebas: `python -m unittest -v`. Sin Docker: definir OPENAI_API_KEY y ejecutar `python orion.py --once`. Los precios de ejecución son aproximados, con comisiones y deslizamiento simulados. El stop es muestreado, no garantizado. Pendientes: backtest, noticias, panel y validación externa.
