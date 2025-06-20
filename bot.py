import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from stripe_client import cancelar_suscripcion_por_customer_id

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 6130272246
GRUPO_CHAT_ID = -4978014065
GHL_API_KEY = os.getenv("GHL_API_KEY")  # 🔐 Guarda esta variable en Railway

# Estado temporal
pending_question = {}

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🛑 Cancelar suscripción", callback_data="cancelar")],
        [InlineKeyboardButton("❓ Tengo otra pregunta", callback_data="pregunta")],
        [InlineKeyboardButton("💳 Consultar mis pagos", callback_data="pagos")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Buscar customer_id desde GHL usando el telegram_id
def buscar_customer_id(telegram_id: int):
    url = f"https://rest.gohighlevel.com/v1/contacts/search?query={telegram_id}"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for contacto in data.get("contacts", []):
                custom_fields = contacto.get("customField", [])
                for campo in custom_fields:
                    if campo.get("key") == "customer_id":
                        return campo.get("value")
        return None
    except Exception as e:
        print(f"Error consultando GHL: {e}")
        return None

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola 👋 ¿Qué deseas hacer?", reply_markup=main_menu())

# Manejo de botones
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat.id

    await query.answer()

    if query.data == "cancelar":
        customer_id = buscar_customer_id(user_id)
        if not customer_id:
            await query.edit_message_text("❌ No encontramos tu registro. Contacta a soporte.")
            return

        success = cancelar_suscripcion_por_customer_id(customer_id)
        if success:
            await query.edit_message_text("✅ Tu suscripción fue cancelada. Ya no se te harán más cargos.")
            try:
                await context.bot.ban_chat_member(chat_id=GRUPO_CHAT_ID, user_id=user_id)
            except Exception as e:
                await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"⚠️ No se pudo expulsar al usuario {user_id}: {e}")
        else:
            await query.edit_message_text("⚠️ No se pudo cancelar. Intenta más tarde.")

    elif query.data == "pregunta":
        pending_question[user_id] = "esperando_pregunta"
        await query.edit_message_text("Por favor, escribe tu pregunta. Un administrador te responderá.")

    elif query.data == "pagos":
        await query.edit_message_text("💳 Esta función estará disponible pronto.")

# Manejo de texto
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if pending_question.get(user_id) == "esperando_pregunta":
        pending_question.pop(user_id)
        mensaje = f"📩 Pregunta de cliente:\nID: {user_id}\nMensaje: {text}"
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=mensaje)
        await update.message.reply_text("Gracias. Un administrador te responderá pronto.")
    else:
        await update.message.reply_text("Selecciona una opción del menú:", reply_markup=main_menu())

# Lanzar bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot activo en Railway")
    app.run_polling()