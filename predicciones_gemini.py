import requests
import json
import os

# === CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ===
API_KEY = os.getenv("API_KEY", "AIzaSyAUS59hYTX6qK9FjGI2ObQpq8ryBjoMGFU")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "6027941537:AAH7ovoZ4Jq8dXl3OckeBodNgPl5QWtiRTY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5284037725")  # tu chat ID

# === FUNCIÓN PARA CONSULTAR GEMINI ===
def get_predictions():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

    prompt = """
    Dame exactamente 5 predicciones deportivas para hoy,
    en formato JSON con este esquema:
    [
      {"partido": "Equipo1 vs Equipo2", "mercado": "Ambos anotan", "probabilidad": 85},
      {"partido": "Equipo3 vs Equipo4", "mercado": "Over 2.5 goles", "probabilidad": 82}
    ]
    Solo incluye predicciones con probabilidad >= 80%.
    Responde ÚNICAMENTE con JSON válido, sin texto adicional.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, json=payload)
    result = response.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip().replace("```json", "").replace("```", "")
        predictions = json.loads(text)
        formatted = "\n".join(
            [f"⚽ {p['partido']} | {p['mercado']} | {p['probabilidad']}%" for p in predictions]
        )
        return formatted
    except Exception as e:
        return f"❌ Error al procesar respuesta: {e}\n{result}"

# === FUNCIÓN PARA ENVIAR A TELEGRAM ===
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message[:4000]}
    r = requests.post(url, data=payload)
    print("Telegram response:", r.json())

# === MAIN ===
def main():
    predictions = get_predictions()
    send_to_telegram(f"📊 Predicciones del día:\n\n{predictions}")

# Ejecutar automáticamente cuando la función se invoque
if __name__ == "__main__":
    main()
