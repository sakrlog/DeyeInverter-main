import gkeepapi
import configparser

configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

keep_username=configParser.get('DeyeInverter', 'keep_username')
# You can only used the below if you have a token
keep_token=configParser.get('DeyeInverter', 'keep_token')

keep = gkeepapi.Keep()

# For your first time, uncomment the below
# fill you credentials, and get your token.
# success = keep.login(username, 'google_apps_password')
# token = keep.getMasterToken()
# print(token)


keep.resume(keep_username,keep_token)

system_notes_id=configParser.get('DeyeInverter', 'system_notes_id')
batteries_notes_id=configParser.get('DeyeInverter', 'batteries_notes_id')
pv_notes_id=configParser.get('DeyeInverter', 'pv_notes_ip')


# System
system_blueprint = 'Grid status: {0}.       Grid Voltage: {1} V\nTemperature: {2} C'
filled_system = system_blueprint.format(1, 220, 10.7)
snote = keep.get(system_notes_id)
snote.text = filled_system


# Batteries
batteries_blueprint = 'Voltage: {0} V.       Status: {1} .\nWatts: {2} W.       SOC: {3} %.'
filled_batteries = batteries_blueprint.format(56, 'charging', -1652, 96)
bnote = keep.get(batteries_notes_id)
bnote.text = filled_batteries

# PV
pv_blueprint = 'PV1: {0} W.       PV2: {1} W.\nTotal: {2} W.'
filled_pv = pv_blueprint.format(2009, 2799, 4710)
pvnote = keep.get(pv_notes_id)
pvnote.text = filled_pv


keep.sync()