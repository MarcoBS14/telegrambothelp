import os
import requests
from dotenv import load_dotenv

load_dotenv()

GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_BASE_URL = "https://rest.gohighlevel.com/v1"

HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Content-Type": "application/json"
}

# 1. Buscar contacto por correo
def obtener_contacto_por_email(email: str):
    url = f"{GHL_BASE_URL}/contacts/search?email={email}"
    response = requests.get(url, headers=HEADERS)

    if response.ok:
        data = response.json()
        if data["contacts"]:
            return data["contacts"][0]
    return None

# 2. Guardar chat_id en contacto existente
def guardar_chat_id(email: str, chat_id: str):
    contacto = obtener_contacto_por_email(email)
    if not contacto:
        print("❌ Contacto no encontrado en GHL.")
        return False

    contact_id = contacto["id"]

    data = {
        "customField": {
            "telegram_chat_id": chat_id
        }
    }

    url = f"{GHL_BASE_URL}/contacts/{contact_id}"
    response = requests.put(url, headers=HEADERS, json=data)

    if response.ok:
        print("✅ chat_id guardado correctamente.")
        return True
    else:
        print("❌ Error al guardar chat_id:", response.text)
        return False

# 3. Obtener chat_id por correo
def obtener_chat_id_por_email(email: str):
    contacto = obtener_contacto_por_email(email)
    if contacto:
        return contacto.get("customField", {}).get("telegram_chat_id")
    return None

# 4. Obtener email por chat_id (nuevo para corregir error)
def obtener_email_por_chat_id(chat_id: str):
    url = f"{GHL_BASE_URL}/contacts"
    response = requests.get(url, headers=HEADERS)
    if response.ok:
        contactos = response.json().get("contacts", [])
        for contacto in contactos:
            if contacto.get("customField", {}).get("telegram_chat_id") == chat_id:
                return contacto.get("email")
    return None

# 5. Actualizar estado a 'cancelado'
def actualizar_estado_cancelado(email: str):
    contacto = obtener_contacto_por_email(email)
    if not contacto:
        print("❌ No se encontró el contacto para cancelar.")
        return False

    contact_id = contacto["id"]
    data = {
        "customField": {
            "estado": "cancelado"
        }
    }

    url = f"{GHL_BASE_URL}/contacts/{contact_id}"
    response = requests.put(url, headers=HEADERS, json=data)

    if response.ok:
        print("✅ Contacto actualizado a 'cancelado'.")
        return True
    else:
        print("❌ Error al actualizar estado:", response.text)
        return False