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
good_low = 		[ (0,255,0) ]  		#AQI 0-24
#good_high = 	[ (127,255,0) ] 	#AQI 25-50
#moderate_low = 	[ (255,255,0) ] 	#AQI 51-75n
#moderate_high = [ (255,200,0) ] 	#AQI 76-100
#UFSI_low = 		[ (255,127,0) ] 	#AQI 101-125
#UFSI_high = 	[ (255,75,0) ] 		#AQI 126-150
unhealthy = 	[ (255,0,0) ] 		#AQI 151+

pm = pm_10min = 0
ledColor = [ (0,0,0) ]

brightness = 1

def fadeToColor(_oldColor, _newColor, bidrectional=True):
	steps = 30
	oldColor = list(_oldColor[0])
	newColor = list(_newColor[0])

	colorChanger = [0,0,0]

	for i in range(steps+1):
		colorChanger[0] = ((oldColor[0] * (steps - i)) + (newColor[0] * i)) / steps
		colorChanger[1] = ((oldColor[1] * (steps - i)) + (newColor[1] * i)) / steps
		colorChanger[2] = ((oldColor[2] * (steps - i)) + (newColor[2] * i)) / steps

		pixels = [(colorChanger[0], colorChanger[1], colorChanger[2])] * (numLEDs/2)
		client.put_pixels(pixels)

		time.sleep(1/30.0)

	if bidrectional:
		for i in range(steps+1):
			colorChanger[0] = ((newColor[0] * (steps - i)) + (oldColor[0] * i)) / steps
			colorChanger[1] = ((newColor[1] * (steps - i)) + (oldColor[1] * i)) / steps
			colorChanger[2] = ((newColor[2] * (steps - i)) + (oldColor[2] * i)) / steps

			pixels = [(colorChanger[0], colorChanger[1], colorChanger[2])] * (numLEDs/2)
			client.put_pixels(pixels)

			time.sleep(1/30.0)

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

		#set static color
		pixels = ledColor * numLEDs
		client.put_pixels(pixels)

		print 'pm_now: ' + str(pm)
		print 'pm_10min: ' + str(pm_10min)
		print 'ledColor: ' + str(ledColor)

		#flash direction of AQI change every 15s if vel of change is high enough
		for i in range(8):
			if abs(pm - pm_10min) > 1.0:
				if pm < pm_10min:
					fadeToColor(ledColor, good_low, True)
				else:
					fadeToColor(ledColor, unhealthy, True)

			time.sleep(15)

def cleanup():
	pixels = [(0,0,0)] * numLEDs
	client.put_pixels(pixels)

def main():
	try:
		update()
	finally:
		cleanup()

if __name__=='__main__':
	main()
