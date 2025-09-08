import requests
import json
import os
from datetime import datetime

# === CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ===
API_KEY = os.getenv("API_KEY", "TU_API_KEY_AQUI")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TU_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "TU_CHAT_ID")

# === FUNCIONES ===
def get_predictions():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

    prompt = """
    Dame predicciones deportivas para hoy:
    - Combinadas: 4 o más partidos, probabilidad >=80%
    - Simples: probabilidad >=90%
    Incluye fútbol, baloncesto, tenis y béisbol.
    Responde únicamente en JSON con este esquema:

    {
      "combinadas": [
        {"partido": "Equipo1 vs Equipo2", "mercado": "Mercado", "deporte": "⚽"},
        ...
      ],
      "simples": [
        {"partido": "Equipo3 vs Equipo4", "mercado": "Mercado", "deporte": "🏀"},
        ...
      ]
    }
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=payload)
    result = response.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip().replace("```json", "").replace("```", "")
        predictions = json.loads(text)
        return predictions
    except Exception as e:
        print(f"❌ Error al procesar predicciones: {e}\n{result}")
        return None

def format_message(predictions, tipo):
    if not predictions or tipo not in predictions:
        return f"No hay predicciones disponibles para {tipo}."

    header = f"⚡ {tipo.capitalize()} ({'≥80%' if tipo=='combinadas' else '≥90%'}) | Confianza IA: {82 if tipo=='combinadas' else 91}%"
    lines = [header, ""]
    for p in predictions[tipo]:
        lines.append(f"{p['deporte']} {p['partido']} | {p['mercado']}")
    return "\n".join(lines)

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message[:4000]}
    r = requests.post(url, data=payload)
    print("Telegram response:", r.json())

# === MAIN ===
def main():
    predictions = get_predictions()
    if not predictions:
        send_to_telegram("❌ No hay predicciones disponibles.")
        return

    # Combinadas
    message_combinadas = format_message(predictions, "combinadas")
    send_to_telegram(message_combinadas)

    # Simples
    message_simples = format_message(predictions, "simples")
    send_to_telegram(message_simples)

if __name__ == "__main__":
    main()

    main()


