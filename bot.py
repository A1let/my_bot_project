from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я ваш бот.")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

def main():
    # Создаём приложение
    application = Application.builder().token("8166850462:AAE7_7MynEpYk4ucffJymiG9SZxyxx3qcHQ").build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Добавляем обработчик сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
