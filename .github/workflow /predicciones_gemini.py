import requests
import json
import os
from datetime import datetime

# === CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ===
API_KEY = os.getenv("API_KEY")  # tu API de Gemini
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # token de Telegram
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # ID del chat

# === FUNCIONES ===

def get_predictions():
    """
    Consulta a Gemini y devuelve predicciones filtradas y resumidas.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

    prompt = """
    Dame 5 predicciones deportivas para hoy en JSON.
    Solo incluye partidos con probabilidad >=80%.
    Formato JSON:
    [
      {"partido": "Equipo1 vs Equipo2", "mercado": "Ambos anotan", "probabilidad": 85, "cuota": 1.6, "analisis": "Breve análisis"},
      {"partido": "Equipo3 vs Equipo4", "mercado": "Over 2.5 goles", "probabilidad": 82, "cuota": 1.8, "analisis": "Breve análisis"}
    ]
    Responde únicamente con JSON válido, sin texto adicional.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload)
        result = response.json()
        print("Respuesta completa de Gemini:", result)  # Para debug

        if "candidates" not in result or len(result["candidates"]) == 0:
            raise ValueError("No hay predicciones disponibles")

        text = result["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip().replace("```json", "").replace("```", "")
        predictions = json.loads(text)

        # Formateo resumido para Telegram
        formatted = "\n".join(
            [f"⚽ {p['partido']} | {p['mercado']} | Cuota: {p['cuota']}" for p in predictions]
        )
        return formatted

    except Exception as e:
        return f"❌ Error al obtener predicciones: {e}\nNo hay predicciones disponibles."

def send_to_telegram(message):
    """
    Envía el mensaje formateado a Telegram.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"📊 Predicciones del día - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n{message}"[:4000]
    }
    r = requests.post(url, data=payload)
    print("Telegram response:", r.json())

# === MAIN ===
if __name__ == "__main__":
    predictions = get_predictions()
    send_to_telegram(predictions)
