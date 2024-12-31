import logging
import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация задач, целей и категорий
DATA_FILE = "data.json"
data = {
    "tasks": [],
    "goals": [],
    "categories": ["Работа", "Учёба", "Здоровье", "Другое"]
}

# Загрузка/сохранение данных
try:
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
except FileNotFoundError:
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я твой помощник. Вот что я умею:\n"
        "/add_task - Добавить задачу\n"
        "/add_goal - Добавить цель\n"
        "/view_tasks - Показать задачи\n"
        "/view_goals - Показать цели\n"
        "/progress - Прогресс за неделю\n"
        "/focus - Фокус-режим (Помодоро)\n"
        "/analyze - Анализ продуктивности\n"
        "/help - Список команд"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Список команд:\n"
        "/add_task - Добавить задачу\n"
        "/add_goal - Добавить цель\n"
        "/view_tasks - Показать задачи\n"
        "/view_goals - Показать цели\n"
        "/progress - Прогресс за неделю\n"
        "/focus - Фокус-режим (Помодоро)\n"
        "/analyze - Анализ продуктивности\n"
        "/help - Список команд"
    )

# Добавление задачи
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        task_name = " ".join(context.args[:-1])
        deadline = context.args[-1]
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
        task = {"name": task_name, "status": "Не начата", "deadline": str(deadline_date)}
        data["tasks"].append(task)
        save_data()
        await update.message.reply_text(f"Задача \"{task_name}\" добавлена с дедлайном {deadline}.")
    except Exception:
        await update.message.reply_text("Использование: /add_task <название задачи> <дедлайн (ГГГГ-ММ-ДД)>")

# Просмотр задач
async def view_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data["tasks"]:
        await update.message.reply_text("У вас нет задач.")
    else:
        response = "Ваши задачи:\n"
        for task in data["tasks"]:
            response += f"- {task['name']} (Статус: {task['status']}, Дедлайн: {task['deadline']})\n"
        await update.message.reply_text(response)

# Добавление цели
async def add_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal_name = " ".join(context.args)
    if not goal_name:
        await update.message.reply_text("Использование: /add_goal <название цели>")
        return

    goal = {"name": goal_name, "subgoals": [], "status": "Не начата"}
    data["goals"].append(goal)
    save_data()
    await update.message.reply_text(f"Цель \"{goal_name}\" добавлена.")

# Просмотр целей
async def view_goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not data["goals"]:
        await update.message.reply_text("У вас нет целей.")
    else:
        response = "Ваши цели:\n"
        for goal in data["goals"]:
            response += f"- {goal['name']} (Статус: {goal['status']})\n"
        await update.message.reply_text(response)

# Прогресс за неделю
async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    completed_tasks = [task for task in data["tasks"] if task["status"] == "Выполнена"]
    total_tasks = len(data["tasks"])
    if total_tasks == 0:
        await update.message.reply_text("У вас нет выполненных задач на этой неделе.")
        return
    progress_percent = len(completed_tasks) / total_tasks * 100
    await update.message.reply_text(f"Ваш прогресс за неделю: {progress_percent:.2f}% выполненных задач.")

# Фокус-режим (Помодоро)
async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Фокус-режим начат: 25 минут работы, 5 минут отдыха. Я напомню, когда закончится.")

    await asyncio.sleep(25 * 60)  # 25 минут работы
    await update.message.reply_text("25 минут прошло! Время отдохнуть 5 минут.")
    await asyncio.sleep(5 * 60)  # 5 минут отдыха
    await update.message.reply_text("5 минут отдыха прошло! Вы готовы продолжать.")

# Анализ продуктивности
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    weekly_tasks = [task for task in data["tasks"] if datetime.strptime(task["deadline"], "%Y-%m-%d").date() >= today - timedelta(days=7)]
    completed_tasks = [task for task in weekly_tasks if task["status"] == "Выполнена"]
    response = f"Анализ продуктивности:\nВсего задач на этой неделе: {len(weekly_tasks)}\nВыполнено: {len(completed_tasks)}\n"
    await update.message.reply_text(response)

# Основная функция
def main():
    application = Application.builder().token("8166850462:AAE7_7MynEpYk4ucffJymiG9SZxyxx3qcHQ").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_task", add_task))
    application.add_handler(CommandHandler("view_tasks", view_tasks))
    application.add_handler(CommandHandler("add_goal", add_goal))
    application.add_handler(CommandHandler("view_goals", view_goals))
    application.add_handler(CommandHandler("progress", progress))
    application.add_handler(CommandHandler("focus", focus))
    application.add_handler(CommandHandler("analyze", analyze))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
