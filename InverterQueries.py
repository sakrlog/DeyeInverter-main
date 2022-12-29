import telebot
import InverterData as Inverter
import time
import configparser
import json

configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

api_key=configParser.get('DeyeInverter', 'queries_bot_api_key')
bot = telebot.TeleBot(api_key)
needed = configParser.get('DeyeInverter', 'needed')

def fecthInverter(text):
    realTime = Inverter.now()
    if(text == True):
        constructed = ''
        for item in realTime:
            if(item in needed):
                constructed += item + ":  " + str(realTime[item]) + "\n"
        return constructed
    else:
        # wanted in json format
        return realTime

@bot.message_handler(commands=['autoUpdate'])
def keepReading(message):
    try:
        fetched = fecthInverter(True)
        lastMessage = fetched
        msg = bot.reply_to(message, fetched)
        i = 0
        while(i<10):
            fetched = fecthInverter(True)
            if(lastMessage != fetched):
                # Telegram doesn't allow sending the same message twice (editing the old one)
                bot.edit_message_text(fetched, chat_id=message.chat.id, message_id=msg.message_id)
                time.sleep(1.5)
                lastMessage = fetched
            i += 1
            time.sleep(0.5)
    except Exception as e:
        bot.send_message(chat_id, text="an error occured in autoUpdate")
        bot.send_message(chat_id, text=e)

@bot.message_handler(commands=['now'])
def oneReading(message):
    try:
        fetched = fecthInverter(True)
        bot.reply_to(message, fetched)
    except Exception as e:
        bot.send_message(chat_id, text="an error occured in now")
        bot.send_message(chat_id, text=e)

@bot.message_handler(commands=['all'])
def AllDetailsNow(message):
    try:
        fetched = fecthInverter(False)
        bot.reply_to(message, json.dumps(fetched))
    except Exception as e:
        bot.send_message(chat_id, text="an error occured in AllDetails")
        bot.send_message(chat_id, text=e)

bot.polling()
