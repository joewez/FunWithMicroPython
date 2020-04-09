#
# kw.py
# simple, standalone app to kill all ESP8266 wifi 
#
import network

ap = network.WLAN(network.AP_IF)    
ap.active(False)

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
while wlan.isconnected():
    pass
