import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno
GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_BASE_URL = "https://rest.gohighlevel.com/v1"

# Headers para autenticación
HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Content-Type": "application/json"
}

# 1. Buscar contacto por correo
def obtener_contacto_por_email(email: str):
    url = f"{GHL_BASE_URL}/contacts/search?email={email}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if data.get("contacts"):
            return data["contacts"][0]
        print("ℹ️ No se encontró contacto con ese correo.")
    except Exception as e:
        print(f"❌ Error al buscar contacto: {e}")
    return None

# 2. Guardar chat_id en campo personalizado
def guardar_chat_id(email: str, chat_id: str):
    contacto = obtener_contacto_por_email(email)
    if not contacto:
        print("❌ Contacto no encontrado en GHL.")
        return False

    contact_id = contacto["id"]

    payload = {
        "customField": {
            "telegram_chat_id": chat_id
        }
    }

    try:
        url = f"{GHL_BASE_URL}/contacts/{contact_id}"
        response = requests.put(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print("✅ chat_id guardado correctamente.")
        return True
    except Exception as e:
        print(f"❌ Error al guardar chat_id: {e}")
        return False

# 3. Obtener chat_id por correo
def obtener_chat_id_por_email(email: str):
    contacto = obtener_contacto_por_email(email)
    if contacto:
        return contacto.get("customField", {}).get("telegram_chat_id")
    return None

# 4. Actualizar estado a 'cancelado'
def actualizar_estado_cancelado(email: str):
    contacto = obtener_contacto_por_email(email)
    if not contacto:
        print("❌ No se encontró el contacto para cancelar.")
        return False

    contact_id = contacto["id"]

    payload = {
        "customField": {
            "estado": "cancelado"
        }
    }

    try:
        url = f"{GHL_BASE_URL}/contacts/{contact_id}"
        response = requests.put(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print("✅ Estado actualizado a 'cancelado'.")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar estado: {e}")
        return False