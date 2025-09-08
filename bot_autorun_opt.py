import requests
import json
import os
from datetime import datetime

# === CREDENCIALES ===
API_KEY = os.getenv("API_KEY", "TU_API_KEY_AQUI")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TU_TELEGRAM_BOT_TOKEN_AQUI")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "TU_TELEGRAM_CHAT_ID_AQUI")

STAKE_BASE = 10
LAST_CHECK_FILE = "last_check.json"

# === FUNCIONES ===
def parse_json_safe(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except:
                continue
    return []

def cargar_last_check():
    if os.path.exists(LAST_CHECK_FILE):
        with open(LAST_CHECK_FILE,"r") as f:
            return json.load(f)
    return {"ultima_fecha":None,"partidos":[]}

def guardar_last_check(data):
    with open(LAST_CHECK_FILE,"w") as f:
        json.dump(data,f)

def obtener_predicciones():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    prompt = """
    Dame 10 predicciones deportivas de hoy (futbol, baloncesto, tenis, beisbol),
    en JSON:
    [{"deporte":"futbol","partido":"Equipo1 vs Equipo2","mercado":"Ambos anotan",
      "probabilidad":85,"cuota":1.45,"analisis":"Comentario","emoji":"⚽"}]
    Solo predicciones >= 80%.
    Responde solo JSON válido.
    """
    payload = {"contents":[{"parts":[{"text":prompt}]}]}
    try:
        res = requests.post(url,json=payload).json()
        text = res["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = text.replace("```json","").replace("```","")
        predicciones = parse_json_safe(text)
        if not isinstance(predicciones,list):
            predicciones=[]
        return [p for p in predicciones if p.get("probabilidad",0)>=80]
    except Exception as e:
        print("❌ Error al obtener predicciones:", e)
        return []

def hay_nuevas_predicciones(predicciones,last_check):
    partidos_actuales = [p["partido"] for p in predicciones]
    partidos_previos = last_check.get("partidos",[])
    nuevas = any(p not in partidos_previos for p in partidos_actuales)
    return nuevas

def generar_apuestas(predicciones):
    combinadas = [p for p in predicciones if 80 <= p.get("probabilidad",0) < 90]
    simples = [p for p in predicciones if p.get("probabilidad",0) >= 90]

    prob_combinada=1
    suma_cuotas=0
    cuotas_product=1
    for p in combinadas:
        prob_combinada*=p.get("probabilidad",0)/100
        suma_cuotas+=p.get("cuota",1)
        cuotas_product*=p.get("cuota",1)
    prob_combinada_pct=round(prob_combinada*100)
    ganancia_combinada=round(STAKE_BASE*cuotas_product,2)

    json_output={
        "fecha":datetime.now().strftime("%Y-%m-%d %H:%M"),
        "apuestas_combinadas":[
            {"partidos":combinadas,"probabilidad_combinada":prob_combinada_pct,
             "suma_cuotas":round(suma_cuotas,2),"stake_recomendado":STAKE_BASE,
             "ganancia_potencial":ganancia_combinada}],
        "apuestas_simples":[
            {**p,"stake_recomendado":STAKE_BASE,
             "ganancia_potencial":round(STAKE_BASE*p.get("cuota",1),2)}
            for p in simples]
    }

    mensaje=f"📊 Predicciones del día - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    if combinadas:
        mensaje+="🔗 Apuesta Combinada ⚡ (≥80%)\n\n"
        for p in combinadas:
            mensaje+=f"{p.get('emoji','')} {p['partido']}\nMercado: {p['mercado']}\nProb: {p['probabilidad']}% | Cuota: {p.get('cuota',1)}\n📌 {p.get('analisis','')}\n\n"
        mensaje+=f"💡 Combinación: Probabilidad {prob_combinada_pct}% | Suma cuotas {round(suma_cuotas,2)} | Stake ${STAKE_BASE} | Ganancia aprox ${ganancia_combinada}\n\n"

    if simples:
        mensaje+="⚡ Apuesta Simple (≥90%)\n\n"
        for p in simples:
            mensaje+=f"{p.get('emoji','')} {p['partido']}\nMercado: {p['mercado']}\nProb: {p['probabilidad']}% | Cuota: {p.get('cuota',1)}\n📌 {p.get('analisis','')}\nStake ${STAKE_BASE} | Ganancia aprox ${round(STAKE_BASE*p.get('cuota',1),2)}\n\n"

    mensaje+="⚠️ Solo fines de prueba/análisis."
    return json_output,mensaje

def enviar_telegram(mensaje):
    url=f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload={"chat_id":TELEGRAM_CHAT_ID,"text":mensaje[:4000]}
    try:
        r=requests.post(url,data=payload)
        print("Telegram response:",r.json())
    except Exception as e:
        print("❌ Error al enviar Telegram:",e)

# === MAIN ===
def main():
    last_check = cargar_last_check()
    predicciones = obtener_predicciones()
    if not predicciones:
        print("No hay predicciones disponibles.")
        return

    if not hay_nuevas_predicciones(predicciones,last_check):
        print("No hay predicciones nuevas desde la última ejecución.")
        return

    json_final,mensaje = generar_apuestas(predicciones)
    with open("dashboard_data.json","w") as f:
        json.dump(json_final,f,indent=2)
    enviar_telegram(mensaje)

    guardar_last_check({"ultima_fecha":datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "partidos":[p["partido"] for p in predicciones]})

if __name__=="__main__":
    main()

