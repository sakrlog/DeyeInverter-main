import traceback
import datetime
import time
import json
import gkeepapi
import configparser
from playwright.sync_api import sync_playwright

configParser = configparser.RawConfigParser()
configFilePath = r'./config.cfg'
configParser.read(configFilePath)

notes_id=configParser.get('phones', 'notes_id')
keep_username=configParser.get('phones', 'keep_username')
alfa_accounts=json.loads(configParser.get('phones', 'alfa_accounts'))
alfa_labels=json.loads(configParser.get('phones', 'alfa_labels'))

keep = gkeepapi.Keep()

# # For your first time, uncomment the below
# # fill you credentials, and get your token.
# # print it, copy it then add to the config
# success = keep.login(keep_username, 'replace_me_with_your_google_app_password')
# token = keep.getMasterToken()
# print(token)

# You can only used the below if you have a token which you should have added to config
keep_token=configParser.get('phones', 'keep_token')

TIMEOUT=int(configParser.get('phones', 'timeout') or 60000 * 5)
REPEAT_MINUTES=int(configParser.get('phones', 'repeat_minutes') or 60)
DANGER_PERCENT=float(configParser.get('phones', 'danger_percent') or 0.8)

def oclock ():
    n = datetime.datetime.now()
    return n.strftime('%Y-%m-%d %H:%M:%S')

def syncInfo(arr=[]):
    if arr:
        keep.resume(keep_username,keep_token)

        danger = False
        text = 'Last Synced at ' + oclock() + '\n'
        
        for data in arr:
            acct_label = alfa_labels.get(data.get("u"), data.get("u"))
            text += f'\nACCT# {data["u"]} ({acct_label})\n'
            
            if data.get('error'):
                text += f' > Error: {data.get("error")}\n'
                continue

            ServiceInformationValue = data['response'].get('ServiceInformationValue')
            for siv in ServiceInformationValue:
                if siv.get('ServiceNameValue') == 'U-share Main' or siv.get('ServiceNameValue') == 'Mobile Internet':
                    ServiceDetailsInformationValue = siv.get('ServiceDetailsInformationValue')[0]
                    ConsumptionValue = ServiceDetailsInformationValue.get('ConsumptionValue')
                    extra_consumed = float(ServiceDetailsInformationValue.get('ExtraConsumptionValue'))
                    
                    acct_consumed = float(ConsumptionValue) 
                    acct_consumed_unit = ServiceDetailsInformationValue.get("ConsumptionUnitValue")
                    if acct_consumed_unit == 'MB':
                        acct_consumed = round(acct_consumed / 1024, 2)
                        acct_consumed_unit = 'GB'
                    
                    package_quota = float(ServiceDetailsInformationValue.get("PackageValue"))
                    package_unit = ServiceDetailsInformationValue.get("PackageUnitValue") 
                    if package_unit == 'MB':
                        package_quota = round(package_quota / 1024, 2)
                        package_unit = 'GB'
                        
                    if acct_consumed / package_quota > DANGER_PERCENT or extra_consumed > 0:
                        danger = True
                    
                    SecondaryValue = ServiceDetailsInformationValue.get('SecondaryValue')

                    if SecondaryValue:
                        total_consumed_calculated = acct_consumed
                        text += f' > {acct_label}: {acct_consumed} {acct_consumed_unit}\n'                    

                        for sv in SecondaryValue:
                            nb_label = alfa_labels.get(sv.get("SecondaryNumberValue"), sv.get("SecondaryNumberValue"))
                            entry_name = sv.get("BundleNameValue")
                            unit = sv.get("ConsumptionUnitValue")
                            consumed = sv.get("ConsumptionValue")
                            if unit == 'MB':
                                consumed = round(float(consumed) / 1024, 2)
                                unit = 'GB'
                            
                            if entry_name == 'Twin-Data Secondary':
                                text += f' > {nb_label}: {consumed} {unit} \n'
                                total_consumed_calculated += consumed
                        
                        text += f' >> TOTAL CONSUMED: {round(total_consumed_calculated, 2)} GB / {package_quota} \n'

                        if total_consumed_calculated / package_quota > DANGER_PERCENT:
                            danger = True
                            
                    else:
                        text += f' >> TOTAL CONSUMED: {acct_consumed} / {package_quota} {package_unit}\n'                    
                    
                    if extra_consumed > 0:
                        text += f' >> !!! EXTRA CONSUMED !!!! {extra_consumed} \n'                    


        note = keep.get(notes_id)
        note.text = text

        # danger if any line is getting close to 90% of its consumption
        if danger:
            note.color = gkeepapi.node.ColorValue.Red
        else:
            note.color = gkeepapi.node.ColorValue.Green

        print("syncing")
        keep.sync()
        print("synced")

def getPhoneData(alfa_account, browser):
    context = browser.new_context()
    context.set_default_navigation_timeout(TIMEOUT)
    context.set_default_timeout(TIMEOUT)
    page = context.new_page()
    print(f'visiting page')
    page.goto('https://www.alfa.com.lb/en/account/login', timeout=TIMEOUT)
    
    page_content = page.text_content('body')
    if 'The requested URL was rejected' in page_content:
        raise ValueError(f"LOGIN PAGE DID NOT LOAD")
    
    print(f'fill form')
    page.fill('#loginForm #Username', alfa_account.get('u'))
    page.fill('#loginForm #Password', alfa_account.get('p'))
    print(f'form filled')
    page.click('#loginForm button[type="submit"]')
    print('clicked login')
    
    page_content = page.text_content('body')
    if 'The requested URL was rejected' in page_content:
        raise ValueError(f"DASHBOARD PAGE DID NOT LOAD")
    
    with page.expect_response("**/en/account/getconsumption*", timeout=TIMEOUT) as response_info:
        print('waiting for the getconsumption response')
        page_content = page.text_content('body')
        if 'The requested URL was rejected' in page_content:
            raise ValueError(f"DASHBOARD PAGE DID NOT LOAD")

    print('response_info done')
    response = response_info.value
    return { **alfa_account, 'response': response.json() }
    
def getPhonesData():
    print('getPhonesData')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=None)
        # browser = p.chromium.launch(headless=False, slow_mo=100)

        arr = []
        for alfa_account in alfa_accounts:
            acct_label = alfa_labels.get(alfa_account.get("u"), alfa_account.get("u"))
            start = datetime.datetime.now()
            print(f'{acct_label} starting...')
            try:
                acct = getPhoneData(alfa_account, browser)
                arr.append(acct)
                end = datetime.datetime.now()
                print(f'{acct_label} loaded in {end - start}')
            except Exception as e:
                print(traceback.format_exc())
                print(f'{acct_label} errored, skipping...')
                arr.append({ **alfa_account, 'error': str(e) })

        browser.close()
        return arr


while(True):
    try:
        arr = getPhonesData()
        syncInfo(arr)
    except Exception as e:
        print(traceback.format_exc())
        print(f'Error, trying again in {REPEAT_MINUTES} minutes')
        print(e)

    # sleep 60 minutes
    print(f'sleeping for {REPEAT_MINUTES} minutes')
    time.sleep(60 * REPEAT_MINUTES)
    