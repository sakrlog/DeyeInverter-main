import datetime
import time
import InverterData as Inverter
hour = datetime.datetime.now().hour


last_status = False

while True:
    # add the battery soc to the if statement
    if 9<hour<16:
        try:
            obj = Inverter.now()
        except:
            print("Inverter fucked up")
            time.sleep(1)
            continue
        if not last_status:
            # This is the first run, last_status is still empty
            last_status = obj
            continue
        elif obj['Battery SOC(%)'] > 95 and obj['Total Load Power(W)'] < 3500:
            # we are sure we have the last status
            # print(str(last_status['Battery Power(W)']) +"//"+ str(obj['Battery Power(W)']))
            # print(abs((obj['Battery Power(W)']*100)/last_status['Battery Power(W)']))
            # print((abs(last_status['Battery Power(W)']) - obj['Battery Power(W)']))
            if obj['Battery Power(W)'] < 0 and (abs(last_status['Battery Power(W)']) + obj['Battery Power(W)']) < 200:
                #it means that we are still charging the batteries
                if obj['Total Load Power(W)'] + abs(obj['Battery Power(W)']) < (obj['PV1 Power(W)'] + obj['PV2 Power(W)']):
                    # PV input is still more than all we want
                    print("PV: " + str(obj['PV1 Power(W)'] + obj['PV2 Power(W)']))
                    print("consumption: " + str(obj['Total Load Power(W)']))
                    print("-- increase --  consumption a bit")
            else:
                print("-- decrease -- consumption a bit")
                #lower the consumption power immediatly
            last_status = obj
    else:
        print("Not in time working conditions code asleep")
    time.sleep(1)
