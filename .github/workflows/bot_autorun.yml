name: Bot Predicciones Horarias

# Ejecuta cada hora (GitHub Actions usa UTC, 7 a.m. Lima = 12 UTC)
on:
  schedule:
    - cron: '0 * * * *'  # cada hora en punto
  workflow_dispatch:   # permite ejecutar manualmente

jobs:
  run-bot:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run bot
        env:
          API_KEY: ${{ secrets.API_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python predicciones_gemini.py
