# https://habr.com/ru/articles/697052/

from dotenv import load_dotenv
import os
from telebot import types
from SKUD_API_moule import get_user_access_by_tg

from Lock import Lock
import telebot
import tinytuya
import time
import json

locks = {
    '505': Lock('505', 6, 'bfc2362c23fa6fe8a32qxv',
                '192.168.137.202', "?mcc<FabE]py;ViN")}
cur_lock = ''

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

users = {}


def save_users():
    users = {}
    for room in locks.keys():
        users[room] = locks[room].get_users()
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

for lock in locks.values():
    lock.sync_users()


def get_menu_markup(user):
    flag = False
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    sync_user_accesses(user)
    for room in locks.keys():
        print(user.username, locks[room].room_id,
              get_user_access_by_tg(user.username, locks[room].room_id))
        if get_user_access_by_tg(user.username, locks[room].room_id):
            reply_markup.row(types.KeyboardButton(f"Настроить доступ к комнате {room}"))
            flag = True
    save_users()
    if not flag:
        reply_markup.row(types.KeyboardButton(f"Синхронизировать доступы"))
    return reply_markup


def sync_user_accesses(user):
    for room in locks.keys():
        if not get_user_access_by_tg(user.username, locks[room].room_id) and \
                str(user.id) in locks[room].get_users().keys():
            locks[room].delete_user(user.id)
        else:
            if str(user.id) not in locks[room].get_users().keys():
                locks[room].add_user(str(user.id))


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, text="Привет, я бот СКУДа. Давай настроим свои доступы!",
                     reply_markup=get_menu_markup(message.from_user))


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    global cur_lock
    if 'Настроить доступ к комнате' in message.text:
        room = message.text.split()[-1]
        cur_lock = locks[room]
        if get_user_access_by_tg(message.from_user.username, cur_lock.room_id):
            lock_users = cur_lock.get_users()
            uid = str(message.from_user.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
            sync_user_accesses(message.from_user)
            bot.send_message(message.chat.id, text="Ваш доступ к этой комнате истёк")
            bot.send_message(message.chat.id, text="Выберите функцию", reply_markup=get_menu_markup(message.from_user))
    elif message.text == "Добавить отпечаток в базу замка":
        if cur_lock.add_fingerprint(str(message.from_user.id)):
            bot.send_message(message.chat.id, text="Вы добавили отпечаток пальца",
                             reply_markup=get_menu_markup(message.from_user))
    elif message.text == 'Добавить пропуск в базу замка':
        if cur_lock.add_card(str(message.from_user.id)):
            bot.send_message(message.chat.id, text="Вы добавили карту",
                             reply_markup=get_menu_markup(message.from_user))
    elif message.text == "Удалить отпечаток из базы замка":
        cur_lock.delete_fingerprint(str(message.from_user.id))
        bot.send_message(message.chat.id, text="Вы удалили отпечаток пальца",
                         reply_markup=get_menu_markup(message.from_user))
    elif message.text == 'Удалить пропуск из базы замка':
        cur_lock.delete_card(str(message.from_user.id))
        bot.send_message(message.chat.id, text="Вы удалили карту",
                         reply_markup=get_menu_markup(message.from_user))
    elif message.text == 'Назад':
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню",
                         reply_markup=get_menu_markup(message.from_user))
    elif message.text == "Синхронизировать доступы":
        sync_user_accesses(message.from_user)
        bot.send_message(message.chat.id, text="Ваши доступы синхронизированы",
                         reply_markup=get_menu_markup(message.from_user))
    save_users()


bot.infinity_polling()
