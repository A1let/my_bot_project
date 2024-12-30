import json
import datetime
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем задачи из файла
def load_tasks():
    try:
        with open("tasks.json", "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []
    return tasks

# Сохраняем задачи в файл
def save_tasks(tasks):
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# Функция для проверки времени работы бота (с 7:00 до 21:00)
def check_time():
    now = datetime.datetime.now()
    if 7 <= now.hour < 21:
        return True
    return False

# Команда /add для добавления задачи
def add_task(update: Update, context: CallbackContext) -> None:
    if not check_time():
        update.message.reply_text('Я сейчас не работаю, попробуй снова позже.')
        return
    
    task_text = ' '.join(context.args)
    if task_text:
        tasks = load_tasks()
        task = {
            "name": task_text,
            "status": "Не выполнено",
            "deadline": None,  # Место для дедлайна
            "type": "Обычная",  # Или "Ежедневная", если нужна ежедневная задача
            "subtasks": []  # Подзадачи
        }
        tasks.append(task)
        save_tasks(tasks)
        update.message.reply_text(f'Задача "{task_text}" добавлена!')
    else:
        update.message.reply_text('Пожалуйста, укажи задачу после команды /add.')

# Команда /tasks для показа всех задач
def show_tasks(update: Update, context: CallbackContext) -> None:
    if not check_time():
        update.message.reply_text('Я сейчас не работаю, попробуй снова позже.')
        return
    
    tasks = load_tasks()
    if tasks:
        message = "Список задач:\n"
        for i, task in enumerate(tasks, 1):
            message += f"{i}. {task['name']} - Статус: {task['status']}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text('Нет добавленных задач.')

# Завершение задачи
def complete_task(update: Update, context: CallbackContext) -> None:
    if not check_time():
        update.message.reply_text('Я сейчас не работаю, попробуй снова позже.')
        return
    
    try:
        task_id = int(context.args[0]) - 1  # ID задачи (считаем с 1)
        tasks = load_tasks()
        if 0 <= task_id < len(tasks):
            tasks[task_id]["status"] = "Выполнено"
            save_tasks(tasks)
            update.message.reply_text(f'Задача "{tasks[task_id]["name"]}" выполнена!')
        else:
            update.message.reply_text('Задача с таким ID не найдена.')
    except (IndexError, ValueError):
        update.message.reply_text('Пожалуйста, укажи корректный ID задачи.')

# Прогресс за неделю
def weekly_progress(update: Update, context: CallbackContext) -> None:
    if not check_time():
        update.message.reply_text('Я сейчас не работаю, попробуй снова позже.')
        return
    
    tasks = load_tasks()
    completed_tasks = [task for task in tasks if task['status'] == 'Выполнено']
    weekly_percentage = (len(completed_tasks) / len(tasks)) * 100 if tasks else 0
    update.message.reply_text(f'Прогресс за неделю: {weekly_percentage:.2f}%')

# Напоминание о задачах
def remind_tasks(update: Update, context: CallbackContext) -> None:
    if not check_time():
        update.message.reply_text('Я сейчас не работаю, попробуй снова позже.')
        return
    
    tasks = load_tasks()
    reminder_message = "Напоминание о задачах:\n"
    for task in tasks:
        if task['status'] == 'Не выполнено':
            reminder_message += f"{task['name']} - Статус: {task['status']}\n"
    if reminder_message == "Напоминание о задачах:\n":
        reminder_message = "Нет незавершенных задач."
    update.message.reply_text(reminder_message)

# Функция для добавления подзадачи
def add_subtask(update: Update, context: CallbackContext) -> None:
    if not check_time():
        update.message.reply_text('Я сейчас не работаю, попробуй снова позже.')
        return
    
    try:
        task_id = int(context.args[0]) - 1  # ID основной задачи
        subtask_text = ' '.join(context.args[1:])
        tasks = load_tasks()
        if 0 <= task_id < len(tasks) and subtask_text:
            subtask = {"name": subtask_text, "status": "Не выполнено"}
            tasks[task_id]["subtasks"].append(subtask)
            save_tasks(tasks)
            update.message.reply_text(f'Подзадача "{subtask_text}" добавлена в задачу "{tasks[task_id]["name"]}".')
        else:
            update.message.reply_text('Задача с таким ID не найдена или подзадача не указана.')
    except (IndexError, ValueError):
        update.message.reply_text('Пожалуйста, укажи корректный ID задачи и текст подзадачи.')

# Основная функция для запуска бота
def main() -> None:
    # Вставь свой токен сюда
    token = '8166850462:AAE7_7MynEpYk4ucffJymiG9SZxyxx3qcHQ'
    
    updater = Updater(token)
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text("Привет! Я бот для твоих задач.")))
    dispatcher.add_handler(CommandHandler("add", add_task))
    dispatcher.add_handler(CommandHandler("tasks", show_tasks))
    dispatcher.add_handler(CommandHandler("complete", complete_task))
    dispatcher.add_handler(CommandHandler("weekly", weekly_progress))
    dispatcher.add_handler(CommandHandler("remind", remind_tasks))
    dispatcher.add_handler(CommandHandler("subtask", add_subtask))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
