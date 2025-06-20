import os
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

# Cargar las variables de entorno
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 6130272246  # Sustituye con tu ID si es otro

# Estados temporales
pending_question = {}

# Menú principal
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🛑 Cancelar suscripción", callback_data="cancelar")],
        [InlineKeyboardButton("❓ Tengo otra pregunta", callback_data="pregunta")],
        [InlineKeyboardButton("💳 Consultar mis pagos", callback_data="pagos")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start o inicio de interacción
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola 👋 ¿Qué deseas hacer?",
        reply_markup=main_menu()
    )

# Manejar selección de opciones
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    await query.answer()

    if query.data == "cancelar":
        msg = (
            "⚠️ Al cancelar tu suscripción, no se volverán a hacer cargos automáticos.\n\n"
            "¿Estás seguro de que deseas cancelar? En breve recibirás el enlace de confirmación."
        )
        await query.edit_message_text(text=msg)

        # Aquí iría la integración con Stripe para cancelar (basado en el chat_id guardado)
        # Por ahora simulamos la confirmación
        await context.bot.send_message(chat_id=chat_id, text="🔗 Cancela aquí: [enlace de cancelación pendiente]")

    elif query.data == "pregunta":
        pending_question[user_id] = "esperando_pregunta"
        await query.edit_message_text(text="Por favor, escribe tu pregunta. Un administrador te responderá.")

    elif query.data == "pagos":
        await query.edit_message_text(text="💳 Por el momento, esta función está en desarrollo.")

# Manejar texto de preguntas
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if pending_question.get(user_id) == "esperando_pregunta":
        pending_question.pop(user_id)
        mensaje = f"📩 Pregunta de cliente desde el bot de cancelación:\nID: {user_id}\nMensaje: {text}"
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=mensaje)
        await update.message.reply_text("Gracias. Un administrador te responderá pronto.")
    else:
        await update.message.reply_text("Selecciona una opción del menú:", reply_markup=main_menu())

# Iniciar la aplicación
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot de cancelación activo.")
    app.run_polling()