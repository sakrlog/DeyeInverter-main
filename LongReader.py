import telebot
import InverterData as Inverter
import time

api_key = ''
bot = telebot.TeleBot(api_key)

needed = ['Grid Voltage L1(V)', 'Load Voltage(V)', 'Total Load Power(W)', 'Battery Temperature(º)', 'Battery Voltage(V)', 'PV1 Power(W)', 'PV2 Power(W)']

def fecthInverter():
    realTime = Inverter.now()
    constructed = ''
    for item in realTime:
        if(item in needed):
            constructed += item + ":  " + str(realTime[item]) + "\n"
    return constructed

@bot.message_handler(commands=['nowContinue'])
def keepReading(message):
    fetched = fecthInverter
    lastMessage = fetched
    msg = bot.reply_to(message, fetched)
    i = 0
    while(i<10):
        fetched = fecthInverter()
        if(lastMessage != fetched):
            bot.edit_message_text(fetched, chat_id=message.chat.id, message_id=msg.message_id)
            time.sleep(1.5)
            lastMessage = fetched
        i += 1
        time.sleep(0.5)


bot.polling()
