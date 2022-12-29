import telebot
import InverterData as Inverter
import time
import configparser
import datetime

configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

api_key=configParser.get('DeyeInverter', 'monitor_bot_api_key')
bot = telebot.TeleBot(api_key)
needed = configParser.get('DeyeInverter', 'needed')
chat_id = configParser.get('DeyeInverter', 'telegram_group_chat_id')

defaultStatus =  {
    "batteries": {
        "full": -1,
        "almostFull": -1
    },
    "PV": {
        "highVoltage": -1,
    },
    "temp": {
        "battery": 5,
        "DCAC": -1
    },
    "grid": {
        "status": -1,
        "highVoltage": -1,
        "lowVoltage": -1
    }
}

while(True):
    # This will loop every 10 seconds, sending a query to the logger and detecting changes
    timeNow = datetime.datetime.now()
    minute = int(timeNow.strftime("%M"))
    hour = int(timeNow.strftime("%H"))
    day = int(timeNow.strftime("%d"))

    if(hour == 1 and minute == 1):
        lastStatus = defaultStatus

    try:
        realTime = Inverter.now()
    except Exception as e:
        bot.send_message(chat_id, text="an error occured")
        bot.send_message(chat_id, text=e)
    alertMessage = ''
    #negative alert
    if(realTime['DC Temperature(º)'] > 80 or realTime['AC Temperature(º)'] > 80):
        if(lastStatus['temp']['DCAC'] == -1 or (hour - lastStatus['temp']['DCAC']) >= 1):
            alertMessage += 'High Temperature in DC and AC: ' + str(realTime['DC Temperature(º)']) + " ºC\n"
            lastStatus['temp']['DCAC'] = hour

    if(realTime['PV1 Voltage(V)'] > 410 or realTime['PV2 Voltage(V)'] >410):
        if(lastStatus['PV']['highVoltage'] == -1 or (hour - lastStatus['PV']['highVoltage']) >= 1):
            alertMessage += "PV voltage too high: >410 V\n"
            lastStatus['PV']['highVoltage'] = hour

    if(realTime['Battery Temperature(º)'] < 3):
        if(lastStatus['temp']['battery'] == -1 or (day - lastStatus['temp']['battery']) >= 1):
            alertMessage += "Battery temperature is very low: " + str(realTime['Battery Temperature(º)']) + " ºC\n"
            lastStatus['temp']['battery'] = day

    if(realTime['Grid Voltage L1(V)'] > 240):
        if(lastStatus['grid']['highVoltage'] == -1 or (hour - lastStatus['grid']['highVoltage']) >= 1):
            alertMessage += "Very high voltage in grid " + str(realTime['Grid Voltage L1(V)']) + " V\n"
            lastStatus['grid']['highVoltage'] = hour

    if(realTime['Grid Voltage L1(V)'] > 80 and realTime['Grid Voltage L1(V)'] < 180):
        if(lastStatus['grid']['lowVoltage'] == -1 or (hour - lastStatus['grid']['lowVoltage']) >= 1):
            alertMessage += "Low voltage in grid " + str(realTime['Grid Voltage L1(V)']) + " V\n"
            lastStatus['grid']['lowVoltage'] = hour


    #positive alert
    if(realTime['Battery SOC(%)'] == 99 and (realTime['Battery Current(A)'] > -8 and realTime['Battery Current(A)'] < 0)):
        if(lastStatus['batteries']['almostFull'] == -1 or (hour - lastStatus['batteries']['almostFull']) >= 3):
            alertMessage += "Batteries almost full"
            lastStatus['batteries']['almostFull'] = hour

    if(realTime['Battery SOC(%)'] == 100 and (realTime['Battery Current(A)'] > -3 and realTime['Battery Current(A)'] < 0)):
        if(lastStatus['batteries']['full'] == -1 or (hour - lastStatus['batteries']['full']) >= 3):
            alertMessage += "Batteries full"
            lastStatus['batteries']['full'] = hour
            
    if(realTime['Grid Voltage L1(V)'] > 180):
        if(lastStatus['grid']['status'] == -1 or (hour - lastStatus['grid']['status']) >= 3):
            alertMessage += "Ejet l kahraba"
            lastStatus['grid']['status'] = hour
            # Grid is available, reset all infos
            lastStatus['batteries']['almostFull'] = -1
            lastStatus['batteries']['full'] = -1

    if(alertMessage != ''):
        print(alertMessage)
        bot.send_message(chat_id, text=alertMessage)
    time.sleep(10)