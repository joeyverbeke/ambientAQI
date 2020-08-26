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

while True:
    conn = urllib2.urlopen("http://api.thingspeak.com/channels/%s/feeds/last.json?api_key=%s" \
                           % (CHANNEL_ID,READ_API_KEY))

    response = conn.read()
    print "http status code=%s" % (conn.getcode())
    data=json.loads(response)
    print data['field8'],data['created_at']
    conn.close()

    pm = float(data['field8'])

    if pm <= 12:    #good
        ledColor = [ (int(pm * 21), 255, 0) ]
    elif pm <= 35:  #moderate
    	ledColor = [ (255, 255 - int((pm - 12) * 5.65), 0) ]
    elif pm <= 55:  #unhealthy for sensitive individuals
    	ledColor = [ (255, 127 - int((pm - 35) * 6.35), 0) ]
    elif pm <= 150: #unhealthy
        ledColor = [ (255, 0, int((pm - 55) * 2.68)) ]
    else:           #very unhealthy
        ledColor = [ ( 255, 0, 255) ]

    for i in range(numLEDs):
    	pixels = ledColor * numLEDs
    	client.put_pixels(pixels)

    time.sleep(60)
