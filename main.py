import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import urllib.parse
import io
import pandas as pd
import re
import hashlib

TOKEN = '7532741882:AAENZLumHJyXYXImkHv-gflYKxejWmIyDD0'

bot = telebot.TeleBot(TOKEN)

# Хранение идентификаторов сообщений
last_message_id = None
last_user_message_id = None
last_file_hash = None

def fetch_schedule_link():
    url = 'https://politech-nsk.ru/index.php/studentam'
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    keywords = {'расписание', 'на', 'курс'}
    
    for link_tag in soup.find_all('a', href=True):
        link_text = link_tag.get_text(strip=True).lower()
        if keywords.issubset(set(link_text.split())):
            href = link_tag['href']
            full_url = urllib.parse.urljoin(url, href)
            return full_url

    return "Ссылка на расписание не найдена."

def calculate_file_hash(file_data):
    # Рассчитываем хэш файла
    hasher = hashlib.md5()
    hasher.update(file_data)
    return hasher.hexdigest()

def download_file(url):
    response = requests.get(url)
    response.raise_for_status()

    file_data = response.content
    file_hash = calculate_file_hash(file_data)
    
    global last_file_hash
    if file_hash != last_file_hash:
        # Если хэш изменился, обновляем его
        last_file_hash = file_hash
        return io.BytesIO(file_data), True  # Возвращаем файл и флаг обновления
    else:
        return None, False  # Возвращаем None и False, если файл не изменился

def delete_previous_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Failed to delete message: {e}")

# Добавляем кнопку для получения расписания
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    schedule_button = types.KeyboardButton('📅 Получить расписание')
    markup.add(schedule_button)
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку, чтобы получить расписание.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '📅 Получить расписание')
def send_schedule(message):
    global last_message_id, last_user_message_id
    
    # Удаляем предыдущее сообщение пользователя, если оно существует
    # if last_user_message_id:
    #    delete_previous_message(message.chat.id, last_user_message_id)

    # Удаляем предыдущее сообщение бота, если оно существует
    # if last_message_id:
    #    delete_previous_message(message.chat.id, last_message_id)

    # Сохраняем ID текущего сообщения пользователя для последующего удаления
    last_user_message_id = message.message_id

    # Отправляем расписание
    schedule_link = fetch_schedule_link()
    if schedule_link.startswith("Ссылка на расписание"):
        response_message = bot.reply_to(message, schedule_link)
        last_message_id = response_message.message_id
    else:
        file_data, file_updated = download_file(schedule_link)
        if file_updated:
            file_name = f'Расписание.xlsx'
            file_data.seek(0)
            response_message = bot.send_document(message.chat.id, (file_name, file_data))
            last_message_id = response_message.message_id
        else:
            response_message = bot.reply_to(message, "Расписание не изменилось.")
            last_message_id = response_message.message_id

if __name__ == '__main__':
    bot.infinity_polling()
