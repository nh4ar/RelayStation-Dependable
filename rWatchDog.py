from gpio_utils import *
from Constants import *
import rNTPTime
import time
import csv
import struct
import sys
import socket

def watchDog(startDateTime, hostIP, BASE_PORT,  streaming=True, logging=True):
	
	time.sleep(30)

	while True:

		audioHeartbeatFileName = BASE_PATH+"Relay_Station{0}/heartbeatLog/Audio.txt".format(BASE_PORT)
		lineCount = 0
		for line in open(audioHeartbeatFileName).xreadlines(  ): lineCount += 1
			# close(audioHeartbeatFileName)

		print("Audio heartbeat file has %d lines" %(lineCount))

		time.sleep(20) #sleep every 20 secs