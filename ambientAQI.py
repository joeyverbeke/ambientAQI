#!/usr/bin/env python
import urllib2,json
READ_API_KEY='OZUQH57IOWW840PA'
CHANNEL_ID='1103672'

import opc, time
numLEDs = 16

client = opc.Client('localhost:7890')

good_low = 		[ (0,255,0) ]  		#AQI 0-24
good_high = 	[ (127,255,0) ] 	#AQI 25-50
moderate_low = 	[ (255,255,0) ] 	#AQI 51-75
moderate_high = [ (255,200,0) ] 	#AQI 76-100
UFSI_low = 		[ (255,127,0) ] 	#AQI 101-125
UFSI_high = 	[ (255,75,0) ] 		#AQI 126-150
unhealthy = 	[ (255,0,0) ] 		#AQI 151+

pm = 0
ledColor = good_low

brightness = 1

while True:
    conn = urllib2.urlopen("http://api.thingspeak.com/channels/%s/feeds/last.json?api_key=%s" \
                           % (CHANNEL_ID,READ_API_KEY))

    response = conn.read()
    print "http status code=%s" % (conn.getcode())
    data=json.loads(response)
    print data['field8'],data['created_at']
    conn.close()

    pm = float(data['field8'])

    if time.strftime("%H", time.localtime()) >= 22 or time.strftime("%H", time.localtime()) < 1:
        brightness = 0.5
    elif time.strftime("%H", time.localtime()) > 1 and time.strftime("%H", time.localtime()) < 8:
        brightness = 0
    else
        brightness = 1

    if pm <= 12:    #good
        ledColor = [ (int(pm * 21 * brightness), int(255 * brightness), 0) ]
    elif pm <= 35:  #moderate
    	ledColor = [ (int(255 * brightness), int( (255 - int((pm - 12) * 5.65)) * brightness ), 0) ]
    elif pm <= 55:  #unhealthy for sensitive individuals
    	ledColor = [ (int(255 * brightness), int( (127 - int((pm - 35) * 6.35)) * brightness ), 0) ]
    elif pm <= 150: #unhealthy
        ledColor = [ (int(255 * brightness), 0, int((pm - 55) * 2.68 * brightness)) ]
    else:           #very unhealthy
        ledColor = [ (int(255 * brightness), 0, int(255 * brightness)) ]

    for i in range(numLEDs):
    	pixels = ledColor * numLEDs
    	client.put_pixels(pixels)

    time.sleep(60)
