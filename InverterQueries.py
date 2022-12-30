import os
import time
import datetime
import traceback
import logging

import configparser
import telebot
import InverterData as Inverter

configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

logging.basicConfig(encoding='utf-8', level=logging.INFO)

api_key = configParser.get('DeyeInverter', 'queries_bot_api_key')
needed = configParser.get('DeyeInverter', 'needed')

bot = telebot.TeleBot(api_key)

def oclock ():
    n = datetime.datetime.now()
    return n.strftime("%Y-%m-%d %H:%M:%S")

logging.warning(f'{oclock()} InverterQueries process id: {os.getpid()}')

def safe_send_message(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text)
    except:
        logging.warning(traceback.format_exc())

def log_message (event, message):
    logging.info(f'[{oclock()}][/{event}], from_user:{message.from_user.id} ({message.from_user.username})')

def fetch_inverter(pick):
    realTime = Inverter.now()
    constructed = ''
    for item in realTime:
        if(item in needed or not pick):
            constructed += item + ":  " + str(realTime[item]) + "\n"
    return constructed

@bot.message_handler(commands=['autoUpdate'])
def autoUpdate(message):
    log_message('autoUpdate', message)
    try:
        fetched = fetch_inverter(True)
        lastMessage = fetched
        msg = bot.reply_to(message, fetched)
        i = 0
        while(i<10):
            fetched = fetch_inverter(True)
            if(lastMessage != fetched):
                # Telegram doesn't allow sending the same message twice (editing the old one)
                bot.edit_message_text(fetched, chat_id=message.chat.id, message_id=msg.message_id)
                time.sleep(1.5)
                lastMessage = fetched
            i += 1
            time.sleep(0.5)
    except Exception as e:
        logging.warning(traceback.format_exc())
        safe_send_message(chat_id=message.chat.id, text="an error occured in autoUpdate")
        safe_send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['now'])
def oneReading(message):
    log_message('now', message)
    try:
        fetched = fetch_inverter(True)
        bot.reply_to(message, fetched)
    except Exception as e:
        logging.warning(traceback.format_exc())
        safe_send_message(chat_id=message.chat.id, text="an error occured in now")
        safe_send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['all'])
def AllDetailsNow(message):
    log_message('all', message)
    try:
        fetched = fetch_inverter(False)
        bot.reply_to(message, fetched)
    except Exception as e:
        logging.warning(traceback.format_exc())
        safe_send_message(chat_id=message.chat.id, text="an error occured in AllDetailsNow")
        safe_send_message(chat_id=message.chat.id, text=e)

bot.polling()
