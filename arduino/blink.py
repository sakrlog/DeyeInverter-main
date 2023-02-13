# #!/usr/bin/env python3

import pyfirmata
import time
import InverterData as Inverter

if __name__ == '__main__':
    board = pyfirmata.Arduino('/dev/tty.usbmodem14401')
    print("Communication Successfully started")
    board.digital[13].write(0)
    
    while True:
        try:
            treshold = 125
            obj = Inverter.now()
            load = obj['Total Load Power(W)']
            if load > treshold:
                board.digital[13].write(1)
            elif load < treshold:
                board.digital[13].write(0)
            print(obj['Total Load Power(W)'])
            time.sleep(3)
        except Exception as e:
            print("something happened skipping")
            time.sleep(5)