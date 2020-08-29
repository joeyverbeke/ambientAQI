#!/usr/bin/env python
import urllib2, json, opc, time
import numpy as np

#thingspeak
READ_API_KEY='OZUQH57IOWW840PA'
CHANNEL_ID='1103672'

#json
ID='60015'
KEY='OZUQH57IOWW840PA'

numLEDs = 16

client = opc.Client('localhost:7890')

###Stepwise###
#good_low = 		[ (0,255,0) ]  		#AQI 0-24
#good_high = 	[ (127,255,0) ] 	#AQI 25-50
#moderate_low = 	[ (255,255,0) ] 	#AQI 51-75n
#moderate_high = [ (255,200,0) ] 	#AQI 76-100
#UFSI_low = 		[ (255,127,0) ] 	#AQI 101-125
#UFSI_high = 	[ (255,75,0) ] 		#AQI 126-150
#unhealthy = 	[ (255,0,0) ] 		#AQI 151+

pm = pm_10min = 0
ledColor = [ (0,0,0) ]

brightness = 1

#def fadeToColor(oldColor, newColor):
#    colorDifference = np.subtract(newColor, oldColor)
#    index = np.nonzero(colorDifference)
#    colorFader = [[oldColor[0]]
#
#    for i in range(colorDifference[index])
#        oldColor[index] += 1
#        time.sleep(1/30.0)

def update():
    while True:
        conn = urllib2.urlopen("https://www.purpleair.com/json?key=%s&show=%s" \
                               % (KEY,ID))

        response = conn.read()
        print "http status code=%s" % (conn.getcode())
        data=json.loads(response)
        conn.close()

        stats = json.loads(data['results'][0]['Stats']) #get PM2.5 values from json

        pm = float(stats['v1'])
        pm_10min = float(stats['v2'])

        if int(time.strftime("%H", time.localtime())) >= 22:
            brightness = 0.5
        elif int(time.strftime("%H", time.localtime())) < 8:
            brightness = 0.2
        else:
            brightness = 1

        if pm <= 12:    #good
            ledColor = [ (int(pm * 21 * brightness), int(255 * brightness), 0) ]
        elif pm <= 35:  #moderate
        	ledColor = [ (int(255 * brightness), int( (255 - (pm - 12) * 5.65) * brightness ), 0) ]
        elif pm <= 55:  #unhealthy for sensitive individuals
        	ledColor = [ (int(255 * brightness), int( (127 - (pm - 35) * 6.35) * brightness ), 0) ]
        elif pm <= 150: #unhealthy
            ledColor = [ (int(255 * brightness), 0, int((pm - 55) * 2.68 * brightness)) ]
        else:           #very unhealthy
            ledColor = [ (int(255 * brightness), 0, int(255 * brightness)) ]

        for i in range(numLEDs):
        	pixels = ledColor * numLEDs
        	client.put_pixels(pixels)

        print 'ledColor: ' + str(ledColor)

        time.sleep(120)

def cleanup():
    for i in range(numLEDs):
        pixels = [(0,0,0)] * numLEDs
        client.put_pixels(pixels)

def main():
    try:
        update()
    finally:
        cleanup()

if __name__=='__main__':
    main()
