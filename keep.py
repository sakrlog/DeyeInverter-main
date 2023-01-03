import gkeepapi
import configparser
import time
import InverterData as Inverter
import datetime

configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

system_notes_id=configParser.get('DeyeInverter', 'system_notes_id')
batteries_notes_id=configParser.get('DeyeInverter', 'batteries_notes_id')
pv_notes_id=configParser.get('DeyeInverter', 'pv_notes_ip')
keep_username=configParser.get('DeyeInverter', 'keep_username')

# You can only used the below if you have a token
keep_token=configParser.get('DeyeInverter', 'keep_token')

keep = gkeepapi.Keep()

# For your first time, uncomment the below
# fill you credentials, and get your token.
# success = keep.login(username, 'google_apps_password')
# token = keep.getMasterToken()
# print(token)

def oclock ():
    n = datetime.datetime.now()
    return n.strftime('%Y-%m-%d %H:%M:%S')

def syncInfo(data={}):
    if data != {}:
        # print(data)
        keep.resume(keep_username,keep_token)
        
        if data['pv']:
            # PV
            pv_blueprint = 'PV1: {0} W.       PV2: {1} W.\nTotal: {2} W.'
            filled_pv = pv_blueprint.format(*data['pv'])
            pvnote = keep.get(pv_notes_id)
            pvnote.text = filled_pv
        if data['batteries']:
            # Batteries
            batteries_blueprint = 'Voltage: {0} V.       Status: {1}.\nWatts: {2} W.       SOC: {3} %.'
            filled_batteries = batteries_blueprint.format(*data['batteries'])
            bnote = keep.get(batteries_notes_id)
            bnote.text = filled_batteries
        if data['system']:
            # System
            system_blueprint = 'Grid status: {0}.       Loads: {1} W\nTemperature: {2} C'
            filled_system = system_blueprint.format(*data['system'])
            snote = keep.get(system_notes_id)
            snote.text = filled_system
            snote.title = 'System  ' + data['system'][-1]
        print("syncing")
        keep.sync()

while(True):
    try:
        obj = Inverter.now()
        timeNow = oclock()
    except:
        continue
    pv = [obj['PV1 Power(W)'], obj['PV2 Power(W)'], int(obj['PV1 Power(W)'])+int(obj['PV2 Power(W)'])]
    system = [obj['Grid Status()'], obj['Total Load Power(W)'], obj['Battery Temperature(º)'], timeNow]
    batt_status = ''
    if obj['Battery Power(W)'] > 0:
        batt_status = 'Discharging'
    else:
        batt_status = 'Charging'
    batteries = [obj['Battery Voltage(V)'], batt_status, obj['Battery Power(W)'],obj['Battery SOC(%)']]
    data = {'pv': pv, 'system': system, 'batteries': batteries}
    syncInfo(data)
    time.sleep(10)