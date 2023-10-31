import sqlite3
import telebot
from telebot import types
import re
from datetime import datetime
from pytz import timezone

token = "6924824601:AAEfU-aPRgvhcPI_HS_GB51e15Pj0SHs3eY"
bot = telebot.TeleBot(token, parse_mode="HTML", threaded=False)


# curl ^
#   --request POST ^
#   --url https://api.telegram.org/bot6924824601:AAEfU-aPRgvhcPI_HS_GB51e15Pj0SHs3eY/setWebhook ^
#   --header "content-type: application/json" ^
#   --data "{\"url\": \"https://d5dmgqcmuk0sflafjh46.apigw.yandexcloud.net/def\"}"


# con = sqlite3.connect('summ.db')
# cur = con.cursor()
# resone = cur.fetchone()
# resall = cur.fetchall()
# con.commit()
# con.close()


def date(n):
    fulltime = datetime.now(timezone("Europe/Moscow"))
    today = fulltime.strftime("%d.%m.%Y")
    month = fulltime.strftime("%m.%Y")
    if n == 1:
        return today
    elif n == 2:
        return month


def small(message):
    con = sqlite3.connect("summ.db")
    cur = con.cursor()
    cur.execute(f"SELECT money FROM t{message.chat.id} WHERE date LIKE '%{date(2)}'")
    resall = cur.fetchall()
    res = 0
    sub = 0
    add = 0
    for i in resall:
        if i[0] < 0:
            sub += i[0]
        else:
            add += i[0]
        res += i[0]
    bot.send_message(
        message.chat.id, f"Расходы = {sub}\nДоходы = {add}\nПрибыль = {res}"
    )
    con.commit()
    con.close()


def long(message):
    con = sqlite3.connect("summ.db")
    cur = con.cursor()
    cur.execute(
        f"SELECT * FROM t{message.chat.id} WHERE date LIKE '%{date(2)}' ORDER BY date ASC"
    )
    resall = cur.fetchall()
    res = 0
    sub = 0
    add = 0
    finalsub = ""
    finaladd = ""
    for i in resall:
        if i[1] < 0:
            sub += i[1]
            finalsub += f"{i[0]} = {i[1]}\n"
        else:
            add += i[1]

            finaladd += f"{i[0]} = {i[1]}\n"
        res += i[1]

    bot.send_message(
        message.chat.id,
        f"Расходы = {sub}\n\n{finalsub}\n--------------------------------\nДоходы = {add}\n\n{finaladd}\n--------------------------------\nПрибыль = {res}",
    )
    con.commit()
    con.close()


def admin(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Расчет")
    bt2 = types.KeyboardButton("Подробно")
    markup.row(bt1)
    markup.row(bt2)
    bot.send_message(
        message.chat.id,
        "Выбери пункт\nИли укажи товар и сумму\n\nНапример:\nмолоко 500",
        reply_markup=markup,
    )


@bot.message_handler(content_types=["text"])
def start(message):
    con = sqlite3.connect("summ.db")
    cur = con.cursor()
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS t{message.chat.id} (name TEXT, money INTEGER, date TEXT)"
    )
    pat = r"^.*\s[-]?\d+$"
    n = re.fullmatch(pat, message.text)

    if n:
        pat2 = r"\s[-]?\d+$"
        pat3 = r"[-]?\d+$"
        name = re.split(pat2, message.text)[0]
        money = re.findall(pat3, message.text)[0]
        cur.execute(
            f"INSERT INTO t{message.chat.id} (name, money, date) values (?,?,?)",
            (name, money, date(1)),
        )
        bot.send_message(message.chat.id, "Ок")

    elif message.text == "Расчет":
        small(message)

    elif message.text == "Подробно":
        long(message)

    else:
        admin(message)
    con.commit()
    con.close()


def handler(event, _):
    print("handler")
    message = telebot.types.Update.de_json(event["body"])
    bot.process_new_updates([message])
    return {
        "statusCode": 200,
        "body": "!",
    }
    start(message)


# bot.remove_webhook()
# bot.infinity_polling()
