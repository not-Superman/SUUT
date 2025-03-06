import telebot
import openai
import json
import os
from dotenv import load_dotenv

# 🔹 Загрузка API-ключа из файла .env
dotenv_path = os.path.join(os.path.dirname(__file__), 'key.env')
load_dotenv(dotenv_path)

# Загружаем ключи
api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = "7538963631:AAH9vEBhmyxn5vQOEDoduVXdhvme-kRvwSA"

# Настройка OpenAI
openai_client = openai.OpenAI(api_key=api_key)

# Создание бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)
CONTEXT_FILE = "context.json"

print("✅ Бот запущен и готов к работе...")

def load_context():
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}  # Если файл пустой или поврежден, возвращаем пустой словарь
    return {}

# 🔹 Функция сохранения контекста в файл
def save_context(context):
    with open(CONTEXT_FILE, "w", encoding="utf-8") as file:
        json.dump(context, file, ensure_ascii=False, indent=4)

context = load_context()

# Функция для общения с OpenAI
def get_openai_response(user_id, message_text):
    print(f"📩 Новый запрос от {user_id}: {message_text}")  # Логируем входящее сообщение

    # Получаем историю диалога пользователя
    user_history = context.get(str(user_id), [])

    # Добавляем новое сообщение пользователя в историю
    user_history.append({"role": "user", "content": message_text})

    # Оставляем только последние 10 сообщений (чтобы не перегружать контекст)
    user_history = user_history[-10:]

    try:
        ai_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Можно заменить на gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "Ты юридический консультант, отвечай только на основании законодательства."}
            ] + user_history,  # Передаем историю сообщений в OpenAI
            max_tokens=500
        ).choices[0].message.content

        print(f"🤖 Ответ OpenAI: {ai_response}")  # Логируем ответ от OpenAI

        # Добавляем ответ AI в историю
        user_history.append({"role": "assistant", "content": ai_response})

        # Сохраняем обновленный контекст
        context[str(user_id)] = user_history
        save_context(context)

        return ai_response


    except Exception as e:
        error_message = f"❌ Ошибка при обработке запроса: {str(e)}"
        print(error_message)  # Логируем ошибку
        return error_message

# Обработчик команд /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    print(f"👤 Пользователь {user_id} запустил бота.")  # Логируем запуск

    # Очищаем контекст диалога при старте
    context[str(user_id)] = []
    save_context(context)

    bot.reply_to(message, "Привет! Я бот-юрист. Задайте мне вопрос по законодательству.")

# 🔹 Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    print(f"📨 Сообщение от {user_id}: {message.text}")  # Логируем сообщение пользователя

    response = get_openai_response(user_id, message.text)

    bot.reply_to(message, response)
    print(f"📤 Ответ пользователю {user_id}: {response}")  # Логируем отправленный ответ

# 🔹 Запуск бота
bot.polling(none_stop=True)

# Запуск бота
bot.polling(none_stop=True)
