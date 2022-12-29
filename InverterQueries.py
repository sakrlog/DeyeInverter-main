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

def safe_send_message(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print(e)


{"Running Status()": 2, "Total Grid Production(kwh)": 0.0, "Daily Energy Bought(kwh)": 7.1, "Daily Energy Sold(kwh)": 0.0, "Total Energy Bought(kwh)": 0.0, "Total Energy Sold(kwh)": 0.0, "Daily Load Consumption(KWH)": 11.3, "Total Load Consumption(KWH)": 0.0, "DC Temperature(\u00ba)": 47.8, "AC Temperature(\u00ba)": 43.5, "Total Production(KWH)": 0.0, "Alert()": 0, "Daily Production(KWH)": 5.8, "PV1 Voltage(V)": 14.1, "PV1 Current(A)": 0.0, "PV2 Voltage(V)": 0.5, "PV2 Current(A)": 0.0, "Grid Voltage L1(V)": 204.1, "Grid Voltage L2(V)": 0.0, "Load Voltage(V)": 204.0, "Current L1(A)": 0.4, "Current L2(A)": 0.0, "Micro-inverter Power(W)": 0, "Gen-connected Status()": 0, "Gen Power(W)": 0, "Internal CT L1 Power(W)": 990, "Internal CT L2 Power(W)": 0, "Grid Status()": 952, "Total Grid Power(W)": 952, "External CT L1 Power(W)": 952, "External CT L2 Power(W)": 0, "Inverter L1 Power(W)": -85, "Inverter L2 Power(W)": 0, "Total Power(W)": -85, "Load L1 Power(W)": 867, "Load L2 Power(W)": 0, "Total Load Power(W)": 867, "Battery Temperature(\u00ba)": 17.6, "Battery Voltage(V)": 53.5, "Battery SOC(%)": 100, "PV1 Power(W)": 0, "PV2 Power(W)": 0, "Battery Status()": -13, "Battery Power(W)": -13, "Battery Current(A)": -0.25, "Grid-connected Status()": 1, "SmartLoad Enable Status()": 16}
        
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
        print(e)
        safe_send_message(chat_id=message.chat.id, text="an error occured in autoUpdate")
        safe_send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['now'])
def oneReading(message):
    try:
        fetched = fecthInverter(True)
        bot.reply_to(message, fetched)
    except Exception as e:
        print(e)
        safe_send_message(chat_id=message.chat.id, text="an error occured in now")
        safe_send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['all'])
def AllDetailsNow(message):
    try:
        fetched = fecthInverter(False)
        bot.reply_to(message, json.dumps(fetched))
    except Exception as e:
        print(e)
        safe_send_message(chat_id=message.chat.id, text="an error occured in AllDetails")
        safe_send_message(chat_id=message.chat.id, text=e)

bot.polling()
