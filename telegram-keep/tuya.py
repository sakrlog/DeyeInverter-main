import tinytuya
import time

# d = tinytuya.OutletDevice('bfed0af475e65ecf078ier', '192.168.9.188', "6baeac8c9cf73699")
# d = tinytuya.OutletDevice('bf954e508853fe3dd1prha', '192.168.9.', "d33275b930f113e9")
d = tinytuya.OutletDevice('bf511b974ec22862femh5g', '192.168.9.138', "f9658eb46f6c7968")

d.set_version(3.3)
time.sleep(3)
d.turn_on()
data = d.status() 
print('Device status: %r' % data)
time.sleep(4)
d.turn_off()