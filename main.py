# https://habr.com/ru/articles/697052/

from dotenv import load_dotenv
import os
from telebot import types

import telebot
import tinytuya
import time
import json

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

users = {'user_counter': 0, 'users': {}}

if 'users.json' in os.listdir():
    with open('users.json') as f:
        users = json.load(f)
else:
    file = open('users.json', 'w')
    file.close()
print(users)
bot = telebot.TeleBot(BOT_TOKEN)
print('BOT STARTED')
d = tinytuya.OutletDevice('bf45653c868eec068bawzu', '192.168.10.10', '*BVvpBw1JTtz1ky.')
d.set_version(3.3)


def get_start_menu_markup():
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Настроить доступ к комнате")
    reply_markup.add(btn)
    return reply_markup


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, text="Привет", reply_markup=get_start_menu_markup())


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    if message.text == 'Настроить доступ к комнате':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if str(message.from_user.id) in list(users['users'].keys()):
            btn = types.KeyboardButton("Удалить пропуск из базы замка")
        else:
            btn = types.KeyboardButton("Добавить пропуск в базу замка")
        back_button = types.KeyboardButton("Назад")
        markup.add(btn, back_button)
        bot.send_message(message.chat.id, text="Выберите функцию", reply_markup=markup)
    elif message.text == 'Добавить пропуск в базу замка':
        add_card(message)
    elif message.text == 'Удалить пропуск из базы замка':
        delete_card(message)
    elif message.text == 'Назад':
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=get_start_menu_markup())


def add_card(message):
    payload = d.generate_payload(tinytuya.CONTROL, {'1': 'AgAAAAMAZAEAAAE='})
    d._send_receive(payload)
    data = d.receive()
    if 'Av8' in data['dps']['1']:
        bot.send_message(message.chat.id, text="Ты добавил карту")
        users['user_counter'] += 1
        users['users'][str(message.from_user.id)] = users['user_counter']
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
        bot.send_message(message.chat.id, text="Карта добавлена", reply_markup=get_start_menu_markup())
    else:
        bot.send_message(message.chat.id, text="Что-то пошло не так попробуй ещё раз")


def delete_card(message):
    payload = d.generate_payload(tinytuya.CONTROL, {'2': 'AgAAAAMAZAH/'})
    d._send_receive(payload)
    del users['users'][str(message.from_user.id)]
    users['user_counter'] -= 1
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)
    bot.send_message(message.chat.id, text="Карта удалена", reply_markup=get_start_menu_markup())


bot.infinity_polling()
