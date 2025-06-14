import os
from dotenv import load_dotenv
import logging
import datetime
from collections import defaultdict
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === TOKEN DEL BOT ===
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === TEMAS MONITOREADOS ===
MONITORED_TOPICS = ["cross", "jano", "monterrey", "sheinbaum", "femboys"]

# === FECHAS DE ÚLTIMA MENCIÓN (GLOBAL) ===
last_mentions = {topic: datetime.datetime.now() for topic in MONITORED_TOPICS}

# === CONTADORES POR USUARIO Y TEMA ===
# Estructura: { user_id: { "username": str, "temas": { topic: cantidad } } }
user_topic_counts = defaultdict(lambda: {"username": "", "mamadas": defaultdict(int)})

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === FUNCIONES ===

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user = update.effective_user
    user_id = user.id
    username = user.username or user.full_name
    now = datetime.datetime.now()

    found_topics = []

    for topic in MONITORED_TOPICS:
        if topic.lower() in text:
            last_time = last_mentions[topic]
            days_since = (now - last_time).days
            last_mentions[topic] = now

            # Actualiza contador por usuario
            user_topic_counts[user_id]["username"] = username
            user_topic_counts[user_id]["mamadas"][topic] += 1

            found_topics.append((topic, days_since, user_topic_counts[user_id]["mamadas"][topic]))

    for topic, days_since, user_count in found_topics:
        await update.message.reply_text(
            f" Ay we....\n"
            f" DÍAS SIN HABLAR DE '{topic}': 0\n"
            f" Antes: {days_since} día(s).\n"
            f"@{username} lo ha mencionado {user_count} vez/veces."
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    status_msg = " Estado actual de los contadores:\n\n"
    for topic in MONITORED_TOPICS:
        days_since = (now - last_mentions[topic]).days
        status_msg += f"• {topic}: {days_since} día(s) sin mención.\n"
    await update.message.reply_text(status_msg)

async def mis_mamadass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = user_topic_counts.get(user_id)

    if not user_data or not user_data["mamadas"]:
        await update.message.reply_text("No has mencionado ningún tema vigilado aún.")
        return

    msg = f"📊 Contador de mamadas para @{user_data['username']}:\n"
    for topic, count in user_data["mamadas"].items():
        msg += f"– {topic}: {count} vez/veces\n"
    await update.message.reply_text(msg)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " ¡Hola! Soy el bot 'DÍAS SIN HABLAR DE...'\n"
        f"Monitoreo: {', '.join(MONITORED_TOPICS)}.\n\n"
        "Comandos:\n"
        "/status — Ver días sin mención por mamada.\n"
        "/mis_mamadass — Ver cuántas veces has hablado de cada mamada."
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("mis_mamadass", mis_mamadass))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_message))

    print("Bot ejecutándose...")
    app.run_polling()

if __name__ == '__main__':
    main()
