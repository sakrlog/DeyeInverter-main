import gkeepapi
import configparser
import time
import InverterData as Inverter
import datetime
import tinytuya


configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

system_notes_id=configParser.get('DeyeInverter', 'system_notes_id')
merge_all_in_system_notes=configParser.get('DeyeInverter', 'merge_all_in_system_notes')
batteries_notes_id=configParser.get('DeyeInverter', 'batteries_notes_id')
pv_notes_id=configParser.get('DeyeInverter', 'pv_notes_id')
keep_username=configParser.get('DeyeInverter', 'keep_username')

keep = gkeepapi.Keep()

# # For your first time, uncomment the below
# # fill you credentials, and get your token.
# # print it, copy it then add to the config
# success = keep.login(keep_username, 'replace_me_with_your_google_app_password')
# token = keep.getMasterToken()
# print(token)

# You can only used the below if you have a token which you should have added to config
keep_token=configParser.get('DeyeInverter', 'keep_token')

grid_status = 0

# def manageTuya(state):
#     d = tinytuya.OutletDevice('bfed0af475e65ecf078ier', '192.168.9.188', "6baeac8c9cf73699")
#     d.set_version(3.3)
#     print("entered with status")
#     print(state)
#     if state == 'turn_on':
#         d.turn_on()
#     else:
#         d.turn_off()


def oclock ():
    n = datetime.datetime.now()
    return n.strftime('%Y-%m-%d %H:%M:%S')

def syncInfo(data={}):
    if data != {}:
        # print(data)
        keep.resume(keep_username,keep_token)

        snote = keep.get(system_notes_id)
        if merge_all_in_system_notes:
            snote.text = f'Last Synced at {oclock()}\n'
            
        if data['system']:
            # System
            system_blueprint = 'GridStatus: {0} W.       Load: {1} W\nTemperature: {2} C.      Gen: {3} W.'
            filled_system = system_blueprint.format(*data['system'])
            
            if merge_all_in_system_notes:
                snote.text += '\n'
                snote.text += filled_system
            else:
                snote.text = filled_system
                snote.title = 'System ' + data['system'][-1]
                if data['system'][0] > 5 or data['system'][3] > 5:
                    snote.color = gkeepapi.node.ColorValue.Green
                else:
                    snote.color = gkeepapi.node.ColorValue.Gray

        if data['batteries']:
            # Batteries
            batteries_blueprint = 'Batt.Voltage: {0} V.       Batt.Status: {1}.\nBatt. Watts: {2} W.       Batt.SOC: {3} %.'
            filled_batteries = batteries_blueprint.format(*data['batteries'])
            
            ref_note = snote
            if merge_all_in_system_notes:
                snote.text += '\n'
                snote.text += filled_batteries
            else:
                bnote = keep.get(batteries_notes_id)
                bnote.text = filled_batteries
                ref_note = bnote

            if data['batteries'][1] == 'Charging':
                ref_note.color = gkeepapi.node.ColorValue.Green
            else:
                ref_note.color = gkeepapi.node.ColorValue.Red

        if data['pv']:
            # PV
            pv_blueprint = 'PV1: {0} W.       PV2: {1} W.\nPvTotal: {2} W.'
            filled_pv = pv_blueprint.format(*data['pv'])

            if merge_all_in_system_notes:
                snote.text += '\n'
                snote.text += filled_pv
            else:
                pvnote = keep.get(pv_notes_id)
                pvnote.text = filled_pv

        print("syncing")
        keep.sync()

while(True):
    try:
        obj = Inverter.now()
        timeNow = oclock()
    except:
        continue
    pv = [obj['PV1 Power(W)'], obj['PV2 Power(W)'], int(obj['PV1 Power(W)'])+int(obj['PV2 Power(W)'])]
    system = [obj['Grid Status()'], obj['Total Load Power(W)'], obj['Battery Temperature(º)'],obj['Gen Power(W)'], timeNow]
    batt_status = ''
    if obj['Battery Power(W)'] > 0:
        batt_status = 'Discharging'
    else:
        batt_status = 'Charging'
    batteries = [obj['Battery Voltage(V)'], batt_status, obj['Battery Power(W)'],obj['Battery SOC(%)']]
    data = {'pv': pv, 'system': system, 'batteries': batteries}
    syncInfo(data)
    if obj['Grid Status()'] > 5 and grid_status == 0:
        # fi kahraba
        # manageTuya('turn_on')
        grid_status = 1
    elif grid_status == 1 and obj['Grid Status()'] == 0:
        # ken fi kahraba w hala2 rahet
        # manageTuya('turn_off')
        grid_status = 0
    time.sleep(10)