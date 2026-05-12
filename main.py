import machine
import time
import network
import urequests
# --- CONFIGURATION ---WIFI_SSID = "Home"      
# <--- Apna WiFi/Hotspot naam check karein
WIFI_PASS = "66778899"  
# <--- Apna WiFi password check karein
THINGSPEAK_API_KEY = "HM74OAEDTPSQ4MXG" 
# Pin Configuration
inlet_pin = machine.Pin(13, machine.Pin.IN)
outlet_pin = machine.Pin(14, machine.Pin.IN)
relay = machine.Pin(12, machine.Pin.OUT)
turb_sensor = machine.ADC(machine.Pin(34))
turb_sensor.atten(machine.ADC.ATTN_11DB)
# Pulse Counters
p_in = 0
p_out = 0
def irq_in(pin):    
global p_in; p_in += 1
def irq_out(pin):    global p_out; p_out += 1
inlet_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=irq_in)
outlet_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=irq_out)
# --- CONNECT WIFI (With Reset Logic) ---
def connect_wifi():    
wlan = network.WLAN(network.STA_IF)    
wlan.active(False)  # Pehle WiFi band karo    
time.sleep(1)    
wlan.active(True)   # Phir se chalu karo
if not wlan.isconnected():        
print("Connecting to WiFi...", end="")        
wlan.connect(WIFI_SSID, WIFI_PASS)        
# Timeout logic taaki code hang na ho        
timeout = 0                                                                                                                                                                                                
while not wlan.isconnected() and timeout < 20:            
print(".", end="")            
time.sleep(1)            
timeout += 1                
if wlan.isconnected():        
print("\nWiFi Connected! IP:", wlan.ifconfig()[0])    
else:        
print("\nWiFi Connection Failed! Check SSID/Password.")
# Run WiFi connectionconnect_wifi()
# --- MAIN LOOP ---while True:    
p_in = 0; p_out = 0    time.sleep(1)         
flow_in = p_in / 7.5    
flow_out = p_out / 7.5    
voltage = (turb_sensor.read() / 4095) * 3.6        
# Leak Logic (ML Threshold)    
is_leak = (flow_in - flow_out) > 0.3    
relay.value(1 if is_leak else 0)   
 status = "LEAKAGE" if is_leak else "NORMAL"   
print(f"{status} | In:{flow_in:.1f} | Out:{flow_out:.1f} | {voltage:.1f}V")
# Cloud Upload    
try:        
full_url = "https://api.thingspeak.com/update?api_key=" + THINGSPEAK_API_KEY + \                  
 "&field1=" + str(flow_in) + "&field2=" + str(flow_out) + \                   
"&field3=" + str(voltage) + "&field4=" + str(1 if is_leak else 0)                
res = urequests.get(full_url)        
res.close()        
print("Cloud Sync: Success")   
 except:        
print("Cloud Sync: Failed")   
 time.sleep(15)