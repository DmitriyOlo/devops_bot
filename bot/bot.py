#поле для импортирования библиотек
import re
import telebot
import logging
import paramiko
from telebot import types

import os

# логирование

logging.basicConfig(
    filename='telegram_bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# БОТ

bot_token = os.getenv('TOKEN')
bot = telebot.TeleBot(bot_token)

# подключение к RM машине через ssh
host = os.getenv('RM_HOST') 
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

# подключение к DB машине через ssh
dhost = os.getenv('DB_HOST')
dport = os.getenv('DB_PORT_SSH')
dusername = os.getenv('DB_USER')
dpassword = os.getenv('DB_PASSWORD')
database = os.getenv('DB_DATABASE')

# функция для выполнения команды по ssh
def execute_ssh_command(command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        client.close()
        return data.decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка SSH: {str(e)}")
        return f"Ошибка подключения или выполнения команды: {str(e)}"

# функция для выполнения команды по ssh to DATABASE
def execute_db_command(command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=dhost, username=dusername, password=dpassword, port=dport)
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        client.close()
        return data.decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка SSH: {str(e)}")
        return f"Ошибка подключения или выполнения команды: {str(e)}"

# для длинных сообщений
def send_long_message(chat_id, message, bot, chunk_size=4096):
    for i in range(0, len(message), chunk_size):
        bot.send_message(chat_id, message[i:i + chunk_size])

# поле для регулярных выражений

email_regex = re.compile(r'\b[A-Za-z0-9]+(?:[._%+-][A-Za-z0-9]+)*@[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*(?:\.[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)*\.[A-Za-z]{2,}\b')
#phone_regex = re.compile(r'(?:8|\+7)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
phone_regex = re.compile(r'\b(?:8|\+7)[\s\-]?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b')
password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*()])[A-Za-z0-9!@#$%^&*()]{8,}$')

# функции для поиска

def find_all_emails(text):
    return email_regex.findall(text)

def find_all_phone_numbers(text):
    return phone_regex.findall(text)

def is_strong_password(password):
    return bool(password_regex.match(password))

# обработчики команд

@bot.message_handler(commands=['find_email'])
def request_email_text(message):
    bot.send_message(message.chat.id, "Введите текст, в котором нужно найти email-адреса:")
    bot.register_next_step_handler(message, handle_email_search)

@bot.message_handler(commands=['find_phone_number'])
def request_phone_text(message):
    bot.send_message(message.chat.id, "Введите текст, в котором нужно найти номера телефонов:")
    bot.register_next_step_handler(message, handle_phone_search)

@bot.message_handler(commands=['verify_password'])
def request_password_text(message):
    bot.send_message(message.chat.id, "Введите пароль для проверки сложности:")
    bot.register_next_step_handler(message, handle_password_check)

@bot.message_handler(commands=['get_release'])
def get_release(message):
    command = "cat /etc/*-release"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Информация о релизе:\n{result}")
    logger.info(f"/get_release: {result}")

@bot.message_handler(commands=['get_uname'])
def get_uname(message):
    command = "uname -a"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Информация о системе:\n{result}")
    logger.info(f"/get_uname: {result}")

@bot.message_handler(commands=['get_uptime'])
def get_uptime(message):
    command = "uptime"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Время работы системы:\n{result}")
    logger.info(f"/get_uptime: {result}")

@bot.message_handler(commands=['get_df'])
def get_df(message):
    command = "df -h"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Информация о файловой системе:\n{result}")
    logger.info(f"/get_df: {result}")

@bot.message_handler(commands=['get_free'])
def get_free(message):
    command = "free -h"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Информация об оперативной памяти:\n{result}")
    logger.info(f"/get_free: {result}")

@bot.message_handler(commands=['get_mpstat'])
def get_mpstat(message):
    command = "mpstat -P ALL"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Информация о производительности процессоров:\n{result}")
    logger.info(f"/get_mpstat: {result}")

@bot.message_handler(commands=['get_w'])
def get_w(message):
    command = "w"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Информация о работающих пользователях:\n{result}")
    logger.info(f"/get_w: {result}")

@bot.message_handler(commands=['get_auths'])
def get_auths(message):
    command = "last -n 10"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Последние 10 входов в систему:\n{result}")
    logger.info(f"/get_auths: {result}")

@bot.message_handler(commands=['get_critical'])
def get_critical(message):
    command = "journalctl -p crit -n 5 --no-pager"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Последние 5 критических событий:\n{result}")
    logger.info(f"/get_critical: {result}")

@bot.message_handler(commands=['get_ps'])
def get_ps(message):
    command = "ps aux | head -n 20"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Информация о запущенных процессах:\n{result}")
    logger.info(f"/get_ps: {result}")

@bot.message_handler(commands=['get_ss'])
def get_ss(message):
    command = "ss -tuln"
    result = execute_ssh_command(command)
    bot.send_message(message.chat.id, f"Информация об используемых портах:\n{result}")
    logger.info(f"/get_ss: {result}")

@bot.message_handler(commands=['get_apt_list'])
def get_apt_list(message):
    # Запрос выбора
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Все пакеты", "Поиск пакета")
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_apt_list_choice)

@bot.message_handler(commands=['get_services'])
def get_services(message):
    command = "systemctl list-units --type=service --all"
    result = execute_ssh_command(command)
    message_text = f"Информация о запущенных службах:\n{result}"
    send_long_message(message.chat.id, message_text, bot)
    logger.info(f"/get_services: {result}")

@bot.message_handler(commands=['get_repl_logs'])
def get_repl_logs(message):
    log_command = "cat /var/log/postgresql/postgresql-13-main.log | grep repl | tail -n 20 " 
    log_data = execute_db_command(log_command)
    if log_data:
        send_long_message(message.chat.id, log_data, bot)
        logger.info(f"Отправлены последние строки логов репликации (all).")
    else:
        bot.send_message(message.chat.id, "Логи репликации не найдены или ошибка при получении.")
        logger.error("Не удалось получить логи репликации.")

@bot.message_handler(commands=['get_emails'])
def send_emails(message):
    query = "SELECT * FROM emails;"
    command = f"su - postgres -c \"psql -d {database} -t -A -c '{query}'\""
    email_data = execute_db_command(command)
    if email_data:
        bot.send_message(message.chat.id, "Email адреса:\n" + email_data)
    else:
        bot.send_message(message.chat.id, "Email адреса не найдены.")

@bot.message_handler(commands=['get_phone_numbers'])
def send_phone_numbers(message):
    query = "SELECT * FROM phone_numbers;"
    command = f"su - postgres -c \"psql -d {database} -t -A -c '{query}'\""
    phone_data = execute_db_command(command)
    if phone_data:
        bot.send_message(message.chat.id, "Номера телефонов:\n" + phone_data)
    else:
        bot.send_message(message.chat.id, "Номера телефонов не найдены.")

# Обработчик команды /help

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = """
Доступные команды:
/find_email - найти email-адреса в тексте
/find_phone_number - Найти номера телефонов в тексте
/verify_password - Проверить сложность пароля
/get_release - Информация о релизе операционной системы
/get_uname - Информация об архитектуре процессора, имени хоста и версии ядра
/get_uptime - Время работы системы
/get_df - Состояние файловой системы
/get_free - Состояние оперативной памяти
/get_mpstat - Информация о производительности процессоров
/get_w - Пользователи, работающие в системе
/get_auths - Последние 10 входов в систему
/get_critical - Последние 5 критических событий
/get_ps - Информация о запущенных процессах
/get_ss - Информация об используемых портах
/get_apt_list - Информация об установленных пакетах (все или поиск)
/get_services - Информация о запущенных службах
/get_repl_logs - Получение логов о репликации Master
/get_emails - Получить email из БД
/get_phone_numbers - Получить номера телефонов из БД
/help - Список доступных команд
"""
    bot.send_message(message.chat.id, help_text)

# обработка поиска

def handle_email_search(message):
    emails = find_all_emails(message.text)
    if emails:
        email_text = ', '.join(emails)
        bot.send_message(message.chat.id, f"Найденные email-адреса:\n{email_text}")
        logger.info(f"Найдены email-адреса: {emails}")
        msg = bot.send_message(message.chat.id, "Сохранить найденные email в БД? Ответьте 'да' или 'нет'")
        bot.register_next_step_handler(msg, save_emails, emails)
    else:
        bot.send_message(message.chat.id, "Не найдено ни одного email-адреса.")
        logger.info("Не найдено ни одного email-адреса.")

def handle_phone_search(message):
    phone_numbers = find_all_phone_numbers(message.text)
    if phone_numbers:
        phone_numbers_text = ', '.join(phone_numbers)
        bot.send_message(message.chat.id, f"Найденные номера телефонов:\n{phone_numbers_text}")
        logger.info(f"Найдены номера телефонов: {phone_numbers}")
        msg = bot.send_message(message.chat.id, "Сохранить найденные номера телефонов в БД? Ответьте 'да' или 'нет'")
        bot.register_next_step_handler(msg, save_phone_numbers, phone_numbers)
    else:
        bot.send_message(message.chat.id, "Не найдено ни одного номера телефона.")
        logger.info("Не найдено ни одного номера телефона.")

def handle_password_check(message):
    password = message.text
    if is_strong_password(password):
        bot.send_message(message.chat.id, "Пароль сложный")
        logger.info("Пароль сложный")
    else:
        bot.send_message(message.chat.id, "Пароль простой")
        logger.info("Пароль простой")

def handle_apt_list_choice(message):
    if message.text == "Все пакеты":
        command = "apt list --installed"
        result = execute_ssh_command(command)
        send_long_message(message.chat.id, f"Установленные пакеты:\n{result}", bot)
        logger.info(f"/get_apt_list (все пакеты): {result}")
    elif message.text == "Поиск пакета":
        bot.send_message(message.chat.id, "Введите название пакета для поиска:")
        bot.register_next_step_handler(message, handle_package_search)
    else:
        bot.send_message(message.chat.id, "Неверный выбор, попробуйте снова.")
        get_apt_list(message)

def handle_package_search(message):
    package_name = message.text.strip()
    command = f"dpkg-query -l {package_name} 2>/dev/null || apt-cache show {package_name} 2>/dev/null"
    result = execute_ssh_command(command)
    if result.strip():
        bot.send_message(message.chat.id, f"Информация о пакете {package_name}:\n{result}")
        logger.info(f"/get_apt_list (поиск): {package_name} - {result}")
    else:
        bot.send_message(message.chat.id, f"Пакет {package_name} не найден.")
        logger.info(f"/get_apt_list (поиск): Пакет {package_name} не найден.")

def save_emails(message, emails):
    if message.text.lower() == 'да':
        errors = False
        for email in emails:
            query = f"INSERT INTO emails (email) VALUES ('{email}');"
            result = execute_db_command(f"echo \"{query}\" | su - postgres -c \"psql -d {database} -t -A\"")
            if "ERROR" in result:
                bot.send_message(message.chat.id, f"Ошибка при сохранении email: {email}")
                errors = True
                logger.error(f"Ошибка при сохранении email: {email}")
        if not errors:
            bot.send_message(message.chat.id, "Все email-адреса успешно сохранены.")
        else:
            bot.send_message(message.chat.id, "Возникли ошибки при сохранении некоторых email-адресов.")
    else:
        bot.send_message(message.chat.id, "Сохранение отменено.")

def save_phone_numbers(message, phone_numbers):
    if message.text.lower() == 'да':
        errors = False
        for phone_number in phone_numbers:
            query = f"INSERT INTO phone_numbers (phone_number) VALUES ('{phone_number}');"
            result = execute_db_command(f"echo \"{query}\" | su - postgres -c \"psql -d {database} -t -A\"")
            if "ERROR" in result or not result:
                bot.send_message(message.chat.id, f"Ошибка при сохранении номера телефона: {phone_number}")
                errors = True
        if not errors:
            bot.send_message(message.chat.id, "Все номера телефонов успешно сохранены.")
        else:
            bot.send_message(message.chat.id, "Возникли ошибки при сохранении некоторых номеров телефонов.")
    else:
        bot.send_message(message.chat.id, "Сохранение отменено.")

# Создать клавиатуру
def setup_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    help_button = types.KeyboardButton('/help')
    keyboard.add(help_button)
    return keyboard

# Запуск бота

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = setup_main_keyboard()
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите /help, чтобы получить список доступных команд.", reply_markup=keyboard)

logger.info("Бот запущен.")

bot.polling(none_stop=True)
