import telebot
from Token_for_hackathon import token
from telebot import types
import requests
from bs4 import BeautifulSoup

bot = telebot.TeleBot(token)

inline_keyboard = types.InlineKeyboardMarkup()
titles = []
images = []
def get_html(url: str) -> str:
    headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
    response = requests.get(url, headers=headers)
    return response.text

def get_data(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    news_list = soup.find_all('div', {'class':'ArticleItem'})
    for counter, news in enumerate(news_list):
        news_title = f"{str(counter + 1)}. {news.find('a', {'class':'ArticleItem--name'}).text}"
        if counter == 20:
            break
        title = types.InlineKeyboardButton(news_title, callback_data=counter+1)
        inline_keyboard.add(title)
        titles.append(title.text)
        image = news.find('img').get('src')
        images.append(image)
    
def main():
    from datetime import date
    current_date = date.today()
    notebook_url = f"https://kaktus.media/?lable=8&date={current_date}&order=time"
    get_data(notebook_url)
main()

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Новости: ", reply_markup=inline_keyboard)

@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    chat_id = c.message.chat.id
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    k1 = types.KeyboardButton("Description")
    k2 = types.KeyboardButton("Quit")
    buttons.add(k1, k2)
    msg = bot.send_message(chat_id, "Some title news you can see Description of this news and Photo: ", reply_markup=buttons)
    bot.register_next_step_handler(msg, get_reaction)
    global news_number
    news_number = c.data

@bot.message_handler(content_types=["text"])
def get_reaction(message):
    chat_id = message.chat.id
    if message.text.lower() == "description":         
        bot.send_message(chat_id, titles[int(news_number) - 1].splitlines()[1])
        bot.send_photo(chat_id, images[int(news_number) - 1]) 
    elif message.text.lower() == "quit":
        bot.send_message(chat_id, "До свидания!")

bot.polling()