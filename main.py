# https://habr.com/ru/articles/697052/

from dotenv import load_dotenv
import os
from telebot import types

import telebot
import tinytuya
import time

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
d = tinytuya.OutletDevice('bf45653c868eec068bawzu', '192.168.10.10', '*BVvpBw1JTtz1ky.')
d.set_version(3.3)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    btn2 = types.KeyboardButton("Получить доступ к комнате")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я тестовый бот для твоей статьи для habr.com".format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    if message.text == 'Получить доступ к комнате':
        print('Access granted')
        payload = d.generate_payload(tinytuya.CONTROL, {'1': 'AgAAAAMAZAEAAAE='})
        print(payload)
        d._send_receive(payload)
        bot.send_message(message.chat.id, text="Ты получил доступ")
    else:
        bot.send_message(message.chat.id, text='Что-то не то')


bot.infinity_polling()
