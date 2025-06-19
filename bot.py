# bot.py
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from ghl_client import guardar_chat_id, obtener_email_por_chat_id, actualizar_estado_cancelado
from stripe_client import buscar_customer_id_por_email, cancelar_suscripcion_por_customer_id

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Estados en memoria temporal
esperando_correo = {}
esperando_duda = {}

# Menú principal
menu = ReplyKeyboardMarkup(
    [
        ["1. Ver picks del día"],
        ["2. Tengo una duda"],
        ["3. Cancelar suscripción"]
    ],
    resize_keyboard=True
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    esperando_correo.pop(user_id, None)
    esperando_duda.pop(user_id, None)
    await update.message.reply_text(
        "👋 Bienvenido al bot de clientes de SportPlays.\nPor favor selecciona una opción del menú:",
        reply_markup=menu
    )

# Manejo de mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # 1. Si está respondiendo una duda
    if user_id in esperando_duda:
        mensaje = f"📩 Nueva duda de cliente:\nID: {user_id}\nMensaje: {text}"
        await context.bot.send_message(chat_id=6130272246, text=mensaje)
        await update.message.reply_text("✅ Gracias, un administrador te responderá en breve.")
        esperando_duda.pop(user_id)
        return

    # 2. Si está enviando correo para registrarse
    if user_id in esperando_correo:
        email = text
        chat_id = update.effective_user.id

        ok = guardar_chat_id(email, str(chat_id))
        if ok:
            await update.message.reply_text("✅ Tu cuenta fue registrada exitosamente.")
        else:
            await update.message.reply_text("❌ Hubo un problema al registrar tu cuenta.")
        esperando_correo.pop(user_id)
        return

    # Opciones del menú
    if text == "1. Ver picks del día":
        await update.message.reply_text("📈 Picks del día:\n- Pick 1: ...\n- Pick 2: ...")

    elif text == "2. Tengo una duda":
        esperando_duda[user_id] = True
        await update.message.reply_text("✏️ Por favor, escribe tu duda:")

    elif text == "3. Cancelar suscripción":
        email = obtener_email_por_chat_id(str(user_id))
        if not email:
            await update.message.reply_text("❌ No encontramos tu correo asociado. Por favor registra tu correo primero.")
            esperando_correo[user_id] = True
            return

        customer_id = buscar_customer_id_por_email(email)
        if not customer_id:
            await update.message.reply_text("❌ No encontramos tu cuenta en Stripe. Contacta a soporte.")
            return

        cancelada = cancelar_suscripcion_por_customer_id(customer_id)
        if cancelada:
            actualizar_estado_cancelado(email)
            await update.message.reply_text("✅ Tu suscripción ha sido cancelada. Gracias por haber estado con nosotros.")
        else:
            await update.message.reply_text("❌ No se pudo cancelar la suscripción. Por favor contacta a soporte.")

    else:
        await update.message.reply_text("Por favor selecciona una opción válida del menú.", reply_markup=menu)

# Inicializar bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot de clientes corriendo...")
    app.run_polling()