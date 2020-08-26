#!/usr/bin/env python
import urllib2,json
READ_API_KEY='OZUQH57IOWW840PA'
CHANNEL_ID='1103672'

import opc, time
numLEDs = 8
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

while True:
    conn = urllib2.urlopen("http://api.thingspeak.com/channels/%s/feeds/last.json?api_key=%s" \
                           % (CHANNEL_ID,READ_API_KEY))

    response = conn.read()
    print "http status code=%s" % (conn.getcode())
    data=json.loads(response)
    print data['field8'],data['created_at']
    conn.close()

    pm = float(data['field8'])

    if pm < 6:
    	ledColor = good_low
    elif pm >= 6 and pm < 12:
    	ledColor = good_high
    elif pm >= 12 and pm < 23.5:
    	ledColor = moderate_low
    elif pm >= 23.5 and pm < 35:
    	ledColor = moderate_high
    elif pm >= 35 and pm < 45:
    	ledColor = UFSI_low
    elif pm >= 45 and pm < 55:
    	ledColor = UFSI_high

    for i in range(numLEDs):
    	pixels = ledColor * numLEDs
    	client.put_pixels(pixels)

    time.sleep(30)
