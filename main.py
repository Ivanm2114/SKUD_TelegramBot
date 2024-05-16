# https://habr.com/ru/articles/697052/

from dotenv import load_dotenv
import os
from telebot import types
from SKUD_API_moule import get_user_access_by_email

from Lock import Lock
import telebot
import tinytuya
import time
import json

locks = {'435': Lock('435', 5, 'bf45653c868eec068bawzu',
                     '192.168.137.95', "'sSfG?_+ojZbW+J^"),
         '505': Lock('505', 6, 'bfc2362c23fa6fe8a32qxv',
                     '192.168.137.146', "?mcc<FabE]py;ViN")}
cur_lock = ''

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

users = {}


def save_users():
    global users
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)


if 'users.json' in os.listdir():
    with open('users.json') as f:
        users = json.load(f)
else:
    file = open('users.json', 'w')
    json.dump(users, file)
    file.close()

print(users)
bot = telebot.TeleBot(BOT_TOKEN)
print('BOT STARTED')


def get_start_menu_markup():
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for room in locks.keys():
        reply_markup.row(types.KeyboardButton(f"Настроить доступ к комнате {room}"))
    return reply_markup


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, text="Привет, для регистрации пришли мне свою корпоративную почту")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    global cur_lock
    if '@' in message.text:
        for room in locks.keys():
            if get_user_access_by_email(message.text, locks[room].room_id):
                if str(message.from_user.id) not in locks[room].get_users().keys():
                    locks[room].add_user(str(message.from_user.id))
                    users[room][str(message.from_user.id)] = {}
                    users['emails'][str(message.from_user.id)] = message.text
                save_users()
    if 'Настроить доступ к комнате' in message.text:
        room = message.text.split()[-1]
        cur_lock = locks[room]
        lock_users = cur_lock.get_users()
        uid = str(message.from_user.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if get_user_access_by_email(users['emails'][str(message.from_user.id)], locks[room].room_id):
            if uid in list(lock_users.keys()):
                if 'card' in lock_users[uid].keys():
                    KeyBtn = types.KeyboardButton("Удалить пропуск из базы замка")
                else:
                    KeyBtn = types.KeyboardButton("Добавить пропуск в базу замка")
                if 'fingerprint' in lock_users[uid].keys():
                    FingerBtn = types.KeyboardButton("Удалить отпечаток из базы замка")
                else:
                    FingerBtn = types.KeyboardButton("Добавить отпечаток в базу замка")
            back_button = types.KeyboardButton("Назад")
            markup.row(KeyBtn, FingerBtn)
            markup.row(back_button)
            bot.send_message(message.chat.id, text="Выберите функцию", reply_markup=markup)
        else:
            locks[room].delete_user(str(message.from_user.id))
            del users[room][str(message.from_user.id)]
            bot.send_message(message.chat.id, text="Ваш доступ истёк", reply_markup=get_start_menu_markup())

    elif message.text == "Добавить отпечаток в базу замка":
        if cur_lock.add_fingerprint(str(message.from_user.id)):
            bot.send_message(message.chat.id, text="Вы добавили отпечаток пальца", reply_markup=get_start_menu_markup())
    elif message.text == 'Добавить пропуск в базу замка':
        if cur_lock.add_card(str(message.from_user.id)):
            bot.send_message(message.chat.id, text="Вы добавили карту", reply_markup=get_start_menu_markup())
    elif message.text == "Удалить отпечаток из базы замка":
        cur_lock.delete_fingerprint(str(message.from_user.id))
        bot.send_message(message.chat.id, text="Вы удалили отпечаток пальца", reply_markup=get_start_menu_markup())
    elif message.text == 'Удалить пропуск из базы замка':
        cur_lock.delete_card(str(message.from_user.id))
        bot.send_message(message.chat.id, text="Вы удалили карту", reply_markup=get_start_menu_markup())
    elif message.text == 'Назад':
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=get_start_menu_markup())
    users[cur_lock.get_room()][str(message.from_user.id)] = cur_lock.get_user(str(message.from_user.id))
    save_users()


bot.infinity_polling()
