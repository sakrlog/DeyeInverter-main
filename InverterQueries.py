import os
import time
import json
import math
import logging
import datetime
import traceback

import telebot
import configparser
import InverterData as Inverter

configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

logging.basicConfig(encoding='utf-8', level=logging.INFO)

installed_power = int(configParser.get('DeyeInverter', 'installed_power'))
api_key = configParser.get('DeyeInverter', 'queries_bot_api_key')
needed = configParser.get('DeyeInverter', 'needed')

bot = telebot.TeleBot(api_key)

def oclock ():
    n = datetime.datetime.now()
    return n.strftime('%Y-%m-%d %H:%M:%S')

logging.warning(f'{oclock()} InverterQueries process id: {os.getpid()}')

def safe_send_message(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text)
    except:
        logging.warning(traceback.format_exc())

def log_message (message):
    logging.info(f'[{oclock()}][{message.text}], from_user:{message.from_user.id} ({message.from_user.username})')

def fetch_inverter(pick, format='text'):
    obj = Inverter.now()
    if format == 'json':
        return obj
    if format == 'text':
        constructed = ''
        for item in obj:
            if(item in needed or not pick):
                constructed += f'{item}: {str(obj[item])}\n'
        return constructed

@bot.message_handler(commands=['autoUpdate'])
def auto_update(message):
    log_message(message)
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
        safe_send_message(chat_id=message.chat.id, text='an error occured in autoUpdate')
        safe_send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['now'])
def one_reading(message):
    log_message(message)
    try:
        fetched = fetch_inverter(True)
        bot.reply_to(message, fetched)
    except Exception as e:
        logging.warning(traceback.format_exc())
        safe_send_message(chat_id=message.chat.id, text='an error occured in now')
        safe_send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['all'])
def all_now(message):
    log_message(message)
    try:
        fetched = fetch_inverter(False)
        bot.reply_to(message, fetched)
    except Exception as e:
        logging.warning(traceback.format_exc())
        safe_send_message(chat_id=message.chat.id, text='an error occured in all_now')
        safe_send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['json'])
def all_now_json(message):
    log_message(message)
    try:
        fetched = fetch_inverter(False, format='json')
        bot.reply_to(message, json.dumps(fetched))
    except Exception as e:
        logging.warning(traceback.format_exc())
        safe_send_message(chat_id=message.chat.id, text='an error occured in all_now_json')
        safe_send_message(chat_id=message.chat.id, text=e)

def extract_args(arg):
    return arg.split()[1:]
    
# example, we can answer questions, based on calculations
# maybe even like `dawwer 10` means 'dawwer 10amps' ?
# maybe even like `dawwer ghessele`
# maybe even like `dawwer azan` or without dawwer even
# I am not sure these are correct
devices = {
    'ghessele': 10,
    'neshefe': 10,
    'jelleye': 10,
    'deffeye': 10,
    'azan': 6,
    'mekweye': 6,
    'foren': 10,
    'microwave': 7,
    'seshwar': 7,
    'trumba': 8,
    'elevator': 15,
    'ev': 35,
    '3': 3,
    '6': 6,
    '10': 10,
    '15': 15,
    '20': 20,
}
devices_commands = [f'dawwer_{k}' for k in devices.keys()]

@bot.message_handler(commands=['dawwer'] + devices_commands)
def dawwer(message):
    args = extract_args(message.text.replace('_', ' '))
    amps_or_device = args[0] if len(args) else None
    amps = None
    watts = 2000
    try:
        amps = int(amps_or_device)
    except:
        pass
    if amps:
        watts = amps * 220
    elif amps_or_device and devices.get(amps_or_device):
        amps = devices.get(amps_or_device.strip())
        watts = amps * 220
                        
    log_message(message)
    try:
        fetched = fetch_inverter(False, format='json')

        grid_voltage = fetched['Grid Voltage L1(V)'] or 0
        # grid_connected = fetched['Grid-connected Status()'] or 0

        load_power = fetched['Load L1 Power(W)'] or 0

        # battery_voltage = fetched['Battery Voltage(V)'] or 0
        battery_percentage = fetched['Battery SOC(%)'] or 0

        # pv1_power = fetched['PV2 Power(W)'] or 0
        # pv1_power = fetched['PV1 Power(W)'] or 0
        
        power_pecentage = math.ceil(load_power / installed_power * 100)
        requested_power_pecentage = math.ceil((load_power + watts) / installed_power * 100)

        is_grid = grid_voltage > 150
        
        power_good = False
        battery_good = False

        reply = ''
        if requested_power_pecentage > 90:
            reply += f'\npower_pecentage CRITICAL!! at: {power_pecentage}%'
            reply += f'\nrequested_power is: {requested_power_pecentage}%!!!'
        else:
            power_good = True
            reply += f'\npower at: {power_pecentage}%'
            reply += f'\nrequested_power is: {requested_power_pecentage}%'

        if battery_percentage > 85:
            battery_good = True
            reply += f'\nbattery_percentage:  {battery_percentage}%'
        else:
            reply += f'\nbattery_percentage is low: {battery_percentage}%'

        if is_grid and power_good:
            reply += '\n*Yes, dawwer!* fi kahraba (or moteur)'
        elif battery_good and power_good:
            reply += '\n*Yes, dawwer!* good battery, *bass 3al reye2*'
        elif not battery_good:
            reply += '\n*NO NO*, low battery'
        elif not power_good:
            reply += '\n*NO NO*, too much load already'

        bot.reply_to(message, reply)
    except Exception as e:
        logging.warning(traceback.format_exc())
        safe_send_message(chat_id=message.chat.id, text='an error occured in all_now_json')
        safe_send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['csgo'])
def cs_go(message):
    try:
        bot.reply_to(message, 'AKID AKID AKID')
    except:
        pass
        
commands = [
    telebot.types.BotCommand('/now', 'Short text status'),
] + [
    telebot.types.BotCommand(f'/dawwer_{k}', f'Can add {k}({devices[k]}A)') for k in devices.keys()
] + [
    telebot.types.BotCommand('/dawwer', 'Can add x AMPS?'),
    telebot.types.BotCommand('/csgo', 'Can I play CS?'),
    telebot.types.BotCommand('/all', 'Long text status'),
    telebot.types.BotCommand('/json', 'Long json status'),
]

bot.set_my_commands(commands)        
bot.infinity_polling()
