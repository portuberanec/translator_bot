
from googletrans import *
import telebot
from telebot import types
from config import host, user, password, db_name, bot_token
import pymysql
import Funtions
import random


#Подключение к боту
Bot = telebot.TeleBot(bot_token)

@Bot.message_handler(commands=['start'])
def start(message):
   Funtions.add_buttons_inout()
   markup = Funtions.add_buttons_inout()
   Bot.send_message(message.chat.id, text="Привет, я бот для перевода и заучивания японских слов", reply_markup=markup)

@Bot.message_handler(content_types=['text'])
def func(message):

   Funtions.add_buttons_inout()
   markup = Funtions.add_buttons_inout()

   if (message.text == "Вывод"):
      output(message)

   elif (message.text == "Запись"):
      msg = Bot.send_message(message.chat.id, text="Введите фразу на японском")
      Bot.register_next_step_handler(msg, Funtions.input_phrase)

   else:
      Bot.send_message(message.chat.id, text="Я пока не принимаю таких запросов, нажмите на одну из кнопок ниже", reply_markup=markup)

def output (message): #Создаёт новые кнопки, ожидает ввода этих кнопок

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Вывести всё")
    btn2 = types.KeyboardButton("Рандом")
    markup.add(btn1, btn2)

    msg = Bot.send_message(message.chat.id, text="Выберите вариант вывода", reply_markup=markup)
    Bot.register_next_step_handler(msg, output_post)

    return(markup)

def output_post (message): #Если вывести всё, то выводит все слова, если рандом, то выводит рандомную фразу с ожиданием ввода

    markup = Funtions.add_buttons_inout()

    if (message.text == "Вывести всё"): #Выводит все слова, существующие в базе
        try:
            connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password = password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected to base")

            with connection.cursor() as cursor:
                sql_quarry = "SELECT Word_Jp, Word_Translit, Word_Rus FROM `Words`"
                cursor.execute(sql_quarry)
                rows = cursor.fetchall()
                cursor.close
            for row in rows:
                Bot.send_message(message.chat.id, text='{0} - {1} - {2}'.format(row['Word_Jp'], row['Word_Translit'], row['Word_Rus']), reply_markup=markup)

        except Exception as ex:
            print ("Connection to base failed")
            print(ex)

        Funtions.add_buttons_inout()

    if (message.text == "Рандом"): #Выводит одну рандомную фразу, ожидая, что пользователь введёт перевод
        try:
            connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password = password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected to base")

        
            with connection.cursor() as cursor: #берёт все ID для подсчёта, какой выбрать рандомный
                sql_quarry = "SELECT ID FROM `Phrase`"
                cursor.execute(sql_quarry)
                rowids = cursor.fetchall()
                cursor.close()

            random_list = []
            for rowid in rowids:
               random_list.append(rowid['ID'])

            random_id = random.choice(random_list)

            with connection.cursor() as cursor: #Вставляет рандомный ID
                sql_quarry = "SELECT Phrase_Jp FROM `Phrase` WHERE ID='{0}';".format(random_id)
                cursor.execute(sql_quarry)
                n = cursor.rowcount
                cursor.close
            if (n == 0): #Теоретически может быть ситуация, что ID с таким номером отсутствует (был удалён, например), если так, берётся новый
                random_id = random.randint(min_row, max_row)
                with connection.cursor() as cursor:
                    sql_quarry = "SELECT Phrase_Jp FROM `Phrase` WHERE ID='{0}';".format(random_id)
                    cursor.execute(sql_quarry)
                    row = cursor.fetchone()
                    cursor.close
            else:
               with connection.cursor() as cursor: #Вставляет рандомный ID
                  sql_quarry = "SELECT Phrase_Jp FROM `Phrase` WHERE ID='{0}';".format(random_id)
                  cursor.execute(sql_quarry)
                  row = cursor.fetchone()
                  cursor.close

            msg = Bot.send_message(message.chat.id, text = row['Phrase_Jp'] + " - Введите перевод")
            Bot.register_next_step_handler(msg, check_phrase, random_id)
            print(random_id)


        except Exception as ex:
            print ("Connection to base failed")
            print(ex)

def check_phrase (message, random_id):

   markup = Funtions.add_buttons_inout()

   print(random_id)
   try:
      connection = pymysql.connect(
      host=host,
      port=3306,
      user=user,
      password = password,
      database=db_name,
      cursorclass=pymysql.cursors.DictCursor
      )

      with connection.cursor() as cursor: #Вставляет рандомный ID
         sql_quarry = "SELECT Phrase_Rus FROM `Phrase` WHERE ID='{0}';".format(random_id)
         cursor.execute(sql_quarry)
         row = cursor.fetchone()
         n = cursor.rowcount
         cursor.close

         if (row['Phrase_Rus'] == message.text):
            Bot.send_message(message.chat.id, text = "Вы молодец, всё верно", reply_markup=markup)
         else:
            Bot.send_message(message.chat.id, text = row['Phrase_Rus'] + "\nНеверно, попробуйте следующую фразу", reply_markup=markup)

   except Exception as ex:
      print ("Connection to base failed")
      print(ex)

   Funtions.add_buttons_inout()

Bot.polling(none_stop=True)
