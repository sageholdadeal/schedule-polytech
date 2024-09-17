import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import urllib.parse

TOKEN = '7532741882:AAENZLumHJyXYXImkHv-gflYKxejWmIyDD0'

bot = telebot.TeleBot(TOKEN)

def fetch_schedule_link():
    url = 'https://politech-nsk.ru/index.php/studentam'
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Определяем набор ключевых слов
    keywords = {'расписание', 'на', 'курс'}
    
    # Находим все теги <a> и проверяем их текст и href
    for link_tag in soup.find_all('a', href=True):
        link_text = link_tag.get_text(strip=True).lower()
        if keywords.issubset(set(link_text.split())):
            href = link_tag['href']
            full_url = urllib.parse.urljoin(url, href)
            encoded_url = full_url.replace(' ', '%20')
            return encoded_url

    return "Ссылка на расписание не найдена."

@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    schedule_link = fetch_schedule_link()
    bot.reply_to(message, f"Ссылка на расписание: {schedule_link}")

if __name__ == '__main__':
    bot.infinity_polling()