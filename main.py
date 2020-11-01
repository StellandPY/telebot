from glob import glob
import telebot
import sqlite3
from telebot import types
import time
import datetime
from random import randint
import requests
import json
#Отключение предупреждения Https
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

token = '1318922261:AAG4ae3IVRamnNG89VHNLX4gfZa-XI4zEtA'
bot = telebot.TeleBot(token)

conn = sqlite3.connect('stellbet.db', check_same_thread=False)
cursor = conn.cursor()


try:
    cursor.execute('''CREATE TABLE users
                    (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL , User_ID integer, akt_date date, cls_date date, phone text, active text)
                    ''')
    cursor.execute('''CREATE TABLE static
                        (plus text, minus text)
                        ''')
    cursor.execute('''CREATE TABLE qiwi_pay
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL , User_ID integer, phone TEXT, sum INTEGER, code INTEGER)
                            ''')
except sqlite3.OperationalError:
    pass


@bot.message_handler(commands=['start'])
def start(message):
    date = datetime.date.today()

    act = 'false'

    us_id = str(message.from_user.id)
    args = int(us_id)
    cursor.execute(""" SELECT User_ID FROM users WHERE User_ID = ? """, [args])
    row = cursor.fetchone()

    if row == None:
        cursor.execute('insert into users (User_id, active) values (?, ?)', (args, act))
        #cursor.execute('insert into qiwi_pay (User_id) values (?)', [args])
        print(cursor.execute('select * from users').fetchall())
        conn.commit()
        bot.send_message(message.chat.id, '<b>Привет!</b> \U0001F603 ' + '\n<i>Любишь</i>' + '<b> халяву</b> ?' + '\U0001F60F \n<i>Любишь</i>' + '<b> стримы</b> ?' + '\U0001F60D \n'
                                          '<i>Тогда специально для тебя приготовил разные пин-кодики для игры</i>' + '<b> Warface</b>!\n' 
                                          '<i>Более подробно можешь узнать нажав на кнопу:</i>' + '<b> Помощь</b>. \U0001F60F \U0001F60D', parse_mode='HTML', reply_markup=keyboard())
    else:
        bot.send_message(message.chat.id, '<b>Привет!</b> \U0001F603 ' + '\n<i>Любишь</i>' + '<b> халяву</b> ?' + '\U0001F60F \n<i>Любишь</i>' + '<b> стримы</b> ?' + '\U0001F60D \n'
                                          '<i>Тогда специально для тебя приготовил разные пин-кодики для игры</i>' + '<b> Warface</b>!\n'
                                          '<i>Более подробно можешь узнать нажав на кнопу:</i>' + '<b> Помощь</b>. \U0001F60F \U0001F60D', parse_mode='HTML', reply_markup=keyboard())


@bot.message_handler(commands=['admin'])
def admins(message):
    admin_id = '342646669'
    us_id = str(message.from_user.id)

    if us_id == admin_id:
        bot.send_message(message.from_user.id, 'Вы вошли в админ панель!', reply_markup=key_admin())
    else:
        print('Error')


@bot.message_handler(commands=['vip'])
def vip(message):
    check = cursor.execute(f"SELECT active FROM users WHERE User_ID={message.chat.id}").fetchone()[0]

    if check == 'false':
        phone = cursor.execute(f"SELECT phone FROM users WHERE User_ID={message.chat.id}").fetchone()[0]



        date = datetime.date.today()

        us_id = str(message.from_user.id)
        phone = str('+' + phone)
        sum = 5
        random_code = randint(100000, 999999)
        cursor.execute("""INSERT into qiwi_pay (User_id, phone, sum, code) VALUES (?,?,?,?)""", (us_id, phone, sum, random_code))
        conn.commit()

        #Создание кнопки
        markup_inline = types.InlineKeyboardMarkup()
        btn_1 = types.InlineKeyboardButton(text='Проверить', callback_data='check')
        btn_2 = types.InlineKeyboardButton(text='Отменить', callback_data='exit')
        markup_inline.add(btn_1, btn_2)

        bot.send_message(message.chat.id, 'Счёт\n\nОплата пописки на сумму: 5р\nДата :' + str(date) + '\nСтатус: Не оплачено'
                                          '\n\nОлатите счёт по никнейму QIWI: STELLAND. В комментарий к платежу '
                                          'оставьте: ' + str(random_code), reply_markup=markup_inline)
    elif check == 'true':
        bot.send_message(message.chat.id, 'У Вас уже активированна подписка!', reply_markup=keyboard())


@bot.callback_query_handler(func=lambda call: True)
def result(call):
    if call.data == 'check':
        a = cursor.execute(f"SELECT * FROM qiwi_pay WHERE user_id = {call.message.chat.id}").fetchone()

        if a == None:
            bot.send_message(call.message.chat.id, 'Платёж не найден.', reply_markup=keyboard())

        else:
            try:
                QIWI_TOKEN = 'bbd47d1910aafe32757e56fddee2fe61'
                QIWI_ACCOUNT = '+79094023102'

                s = requests.Session()
                s.headers['authorization'] = 'Bearer ' + QIWI_TOKEN
                parameters = {'rows': '50'}
                h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + QIWI_ACCOUNT + '/payments', params=parameters,
                          verify=False)
                req = json.loads(h.text)
                print(req['data'][0])

                try:
                    phone = cursor.execute(f"""SELECT phone FROM qiwi_pay WHERE user_id = {call.message.chat.id}""").fetchone()[0]
                    random_code = cursor.execute(f"""SELECT code FROM qiwi_pay WHERE user_id = {call.message.chat.id}""").fetchone()[0]
                    sum = cursor.execute(f"""SELECT sum FROM qiwi_pay WHERE user_id = {call.message.chat.id}""").fetchone()[0]

                    # проходимся циклом по словарю
                    for i in range(len(req['data'])):
                        if req['data'][i]['account'] == phone:
                            if req['data'][i]['comment'] == str(random_code):
                                if req['data'][i]['sum']['amount'] == sum:
                                    cursor.execute(f"DELETE FROM qiwi_pay WHERE user_id = {call.message.chat.id}")
                                    cursor.execute(f"""UPDATE users set active='true' WHERE User_id={call.message.chat.id}""")
                                    conn.commit()
                                    bot.edit_message_text(chat_id=call.message.chat.id,
                                                          message_id=call.message.message_id, text="Вы успешно оплатили"
                                                          " подписку!", parse_mode='Markdown')
                                    bot.send_message(call.message.chat.id,
                                                     'Удачных ставок!', reply_markup=keyboard())
                except:
                    bot.send_message(call.message.chat.id, 'Произошла ошибка. Обратитесь в тех.поддержку')
            except:
                bot.send_message(call.message.chat.id, 'Проблемы в работе серверов Qiwi.\nПопробуйте попытку по позже.')

    elif call.data == 'exit':
        a = cursor.execute(f"SELECT * FROM qiwi_pay WHERE user_id = {call.message.chat.id}").fetchone()
        if a == None:
            bot.send_message(call.message.chat.id, 'Платёж не найден.', reply_markup=keyboard())
        else:
            a = cursor.execute(f"DELETE FROM qiwi_pay WHERE user_id = {call.message.chat.id}").fetchone()
            conn.commit()
            bot.send_message(call.message.chat.id, 'Платёж отменён.', reply_markup=keyboard())


@bot.message_handler(content_types=['contact'])
def phone(message):
    if message.contact is not None:
        phone = message.contact.phone_number
        a = cursor.execute(f'SELECT phone FROM users WHERE User_ID={message.chat.id}').fetchone()[0]
        print(a)

        if a == None:
            cursor.execute(f"""UPDATE users set phone={phone} WHERE User_id={message.chat.id}""")
            conn.commit()
            bot.send_message(message.chat.id, 'Номер успешно добавлен в профиль!', reply_markup=keyboard())
        else:
            bot.send_message(message.chat.id, 'У Вас уже введёт номер в профиле!', reply_markup=keyboard())




@bot.message_handler(content_types=["text"])
def text(message):
    admin_id = 342646669

    #Проверяем есть ли пользователь в бд
    us_id = str(message.from_user.id)
    args = int(us_id)
    cursor.execute("""SELECT User_ID FROM users WHERE User_ID = ? """, [args])
    row = cursor.fetchone()

    text = message.text

    if row == None:
        print('Error')
    else:
        if text == "🥇 Прогнозы 🥇":
            #Выьрать все фотки и отправить их
            lists = glob('images/*')

            bot.send_message(message.chat.id, 'FREE', reply_markup=keyboard())

            for i in lists:
                bot.send_photo(message.chat.id, photo=open(i, 'rb'))

        elif text == '🎯 Статистика 🎯':

            cursor.execute("""SELECT count(*) from static WHERE plus=1""")
            row = cursor.fetchall()[0]
            stat_plus = row[0]
            conn.commit()

            cursor.execute("""SELECT count(*) from static WHERE minus=2""")
            row = cursor.fetchall()[0]
            stat_minus = row[0]
            conn.commit()

            bot.send_message(message.chat.id, 'Вот наша статистика за текущий месяц: \nПлюсы:'
                                              ' ' + str(stat_plus) + '\nМинусы: ' + str(stat_minus),
                             reply_markup=keyboard())

        elif text == '🛠 Помощь 🛠':
            bot.send_message(message.chat.id, 'Помощь по боту \U0001F64F', reply_markup=keyboard())

        elif text == '💸 Поддержать автора 💸':
            bot.send_message(message.chat.id, 'ТУТ КАРТЫ И ТД', reply_markup=keyboard())

        elif text == '🏆 Прогнозы ViP 🏆':
            a = cursor.execute(f'SELECT phone FROM users WHERE User_ID={message.chat.id}').fetchone()[0]
            if a == None:
                markup_request = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                    types.KeyboardButton('Отправить свой контакт ☎️', request_contact=True)
                ).add(types.KeyboardButton('Отмена'))
                bot.send_message(message.chat.id, 'У Вас не активированна подписка :( \nХотите её активировать?\n'
                                                  'Нажми на кнопку ниже, и отправь нам свой номер!',
                                                   reply_markup=markup_request)
            else:
                try:
                    us_id = message.from_user.id
                    cursor.execute("""SELECT active FROM users WHERE User_id = ?""", [us_id])
                    row = cursor.fetchone()[0]

                    if row == 'true':
                        # Выьрать все фотки и отправить их
                        lists = glob('vip/*')

                        bot.send_message(message.chat.id, 'VIP', reply_markup=keyboard())

                        for i in lists:
                            bot.send_photo(message.chat.id, photo=open(i, 'rb'))
                    else:
                        bot.send_message(message.chat.id, 'У Вас не активированна подписка :( \nХотите её активировать?\n'
                                                          'Пишите: /vip')

                except:
                    print('Error')

        elif text == 'Отмена':
            bot.send_message(message.chat.id, '🙃', reply_markup=keyboard())

        #-----------------------------------------------------------------------------------
        #Сообщения для администратора
        elif text == '➕ Ставки ➕' and args == admin_id:
            sent = bot.send_message(message.from_user.id, 'Введите кол-во плюсов')
            bot.register_next_step_handler(sent, plus)
        elif text == '➖ Ставки ➖' and args == admin_id:
            sent = bot.send_message(message.from_user.id, 'Введите кол-во минусов')
            bot.register_next_step_handler(sent, minus)
        elif text == '❌ Очистить ❌' and args == admin_id:
            sent = bot.send_message(message.from_user.id, 'Вы действительно хотите очистить историю Статистики?',
                                    reply_markup=key_yesno())
            bot.register_next_step_handler(sent, delete_stat)
        elif text == '📍 Выйти 📍':
            bot.send_message(message.chat.id, 'Вы вышли в главное окно', reply_markup=keyboard())
        else:
            bot.send_message(message.chat.id, 'Я не понял чего ты хочешь :(', reply_markup=keyboard())



def plus(message):
    try:
        text = int(message.text)
        plus = 1

        for i in range(text):
            cursor.execute('insert into static (plus) values (?)', ([plus]))
        conn.commit()
        bot.send_message(message.from_user.id, 'Выполнено успешно добавили ' + str(text) + ' успешных ставки! :)',
                         reply_markup=key_admin())
    except:
        bot.send_message(message.from_user.id, 'Вы ввели что-то не так :(')


def minus(message):
    try:
        text = int(message.text)
        minus = 2

        for i in range(text):
            cursor.execute('insert into static (minus) values (?)', ([minus]))
        conn.commit()
        bot.send_message(message.from_user.id, 'Выполнено успешно добавили ' + str(text) + ' неуспешных ставки! :(',
                         reply_markup=key_admin())
    except:
        bot.send_message(message.from_user.id, 'Выввели что-то не так :(')


def delete_stat(message):
    text = message.text
    if text == 'Да':
        cursor.execute('''DELETE FROM static''')
        conn.commit()
        bot.send_message(message.from_user.id, 'Вы успешно очистили статистику!', reply_markup=key_admin())
    else:
        bot.send_message(message.from_user.id, 'Хорошо что передумали :)', reply_markup=key_admin())


#Клавиатуры
def keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_a1 = types.KeyboardButton('🥇 Прогнозы 🥇')
    btn_b1 = types.KeyboardButton('🏆 Прогнозы ViP 🏆')
    btn_2 = types.KeyboardButton('🎯 Статистика 🎯')
    btn_3 = types.KeyboardButton('🛠 Помощь 🛠')
    btn_4 = types.KeyboardButton('💸 Поддержать автора 💸')
    markup.add(btn_a1, btn_b1)
    markup.add(btn_2, btn_3)
    markup.add(btn_4)
    return markup


def key_admin():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_1 = types.KeyboardButton('➕ Ставки ➕')
    btn_2 = types.KeyboardButton('➖ Ставки ➖')
    btn_3 = types.KeyboardButton('❌ Очистить ❌')
    btn_4 = types.KeyboardButton('📍 Выйти 📍')
    markup.add(btn_1, btn_2)
    markup.add(btn_3)
    markup.add(btn_4)
    return markup


def key_yesno():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_1 = types.KeyboardButton('Да')
    btn_2 = types.KeyboardButton('Нет')
    markup.add(btn_1, btn_2)
    return markup


while True:
    try:
        bot.polling(none_stop=True, timeout=123, interval=0)

    except Exception as E:
        print(E.args)
        time.sleep(2)
