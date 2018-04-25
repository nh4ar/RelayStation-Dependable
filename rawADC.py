from gpio_utils import *
from Constants import *
import rNTPTime
import socket
import time
import csv
import subprocess
import sys


# gets sensor values from the temperature sensor and the microphone, writes the data to a file and sends the data over a socket
def readADC(startDateTime, hostIP, BASE_PORT, streaming = True, logging = True):

	server_address = (hostIP, BASE_PORT)
	# use custom function because datetime.strptime fails in multithreaded applications
	startTimeDT = rNTPTime.stripDateTime(startDateTime)
	audioFileName = BASE_PATH+"Relay_Station{0}/Audio/Audio{1}.txt".format(BASE_PORT, startTimeDT)
	doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)
	tempFileName = BASE_PATH+"Relay_Station{0}/Temperature/Temperature{1}.txt".format(BASE_PORT, startTimeDT)

	rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)
	
	global rawADC_Time
	global rawADC_startDateTime
	rawADC_startDateTime = startDateTime

	sensoMessage = " ADC "

	with open(rawADCFileName, "w") as rawADCFile:
		rawADCFile.write(startDateTime+"\n")
		rawADCFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
		rawADCFile.write("Timestamp,Mic(10kHz samples),Door1(10 samples),Door2(10 samples),Temp(Degree F)\n")
	rawADCFile.close()
		
	# get starting time according to the BBB. This is only used for time deltas
	startTime = datetime.datetime.now()
	
	iterations = 0
	dummyvar = 0

	test_count = 0
	
	sumAudio = 0
	sumDoor1 = 0
	sumDoor2 = 0
	sumTemp = 0

	while True:

		rawADC_Time = startTimeDT
		if iterations >= ADC_LENGTH:

			iterations = 0

			test_count += 1
			# startDateTime = "2017-11-15 %d%d:%d%d:%d%d.000" %(test_count,test_count,test_count,test_count,test_count,test_count)

			#get current time from basestation
			startDateTime = rNTPTime.sendUpdate(server_address, "-99", 5)
			# if startDateTime updates sucessfully -> create a new file
			# if startDateTime == None (update fails) -> keep writing the current file
			if startDateTime != None:
				startTimeDT = rNTPTime.stripDateTime(startDateTime)
				rawADC_Time = startTimeDT
				rawADC_startDateTime = startDateTime

				rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)
				with open(rawADCFileName, "w") as rawADCFile:
					rawADCFile.write(startDateTime+"\n")
					rawADCFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					rawADCFile.write("Timestamp,Mic(10kHz samples),Door1(10 samples),Door2(10 samples),Temp(Degree F)\n")
				rawADCFile.close()

				# get new local start time
				startTime = datetime.datetime.now()

		
		iterations += 1
		dummyvar += 1
		
		# calculate the time since the start of the data collection
		currTime = datetime.datetime.now()
		currTimeDelta = (currTime - startTime).days * 86400 + (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
			
		# run the c code to get one second of data from the ADC
		# proc = subprocess.Popen(["./root/besi-relay-station/BESI_LOGGING_R/ADC1"], stdout=subprocess.PIPE,)
		proc = subprocess.Popen(["./ADC1"], stdout=subprocess.PIPE,)
		# anything printed in ADC.c is captured in output
		output = proc.communicate()[0]
		split_output = output.split(',')
		# try:
		# 	proc = subprocess.Popen(["./ADC1"], stdout=subprocess.PIPE,)
		# 	# anything printed in ADC.c is captured in output
		# 	output = proc.communicate()[0]
		# 	split_output = output.split(',')
		# except :
		# 	print "Thread: ADCThread, ERROR: subprocess.Popen[./ADC1]"
		# 	split_output = [0]*10021
		# 	split_output = ",".join(map(str, split_output))
		# 	split_output = split_output.split(',')


		# print newTimeDelta, (float(split_output[-5]) + currTimeDelta - testTime), len(split_output)
			
		# data is in <timestamp>,<value> format
		# 100 samples/second from the mic and 1 sample/sec from the temperature sensor
		i = 0 
		ka = 0
		sumA = 0
		kd = 0
		sumD1 = 0
		sumD2 = 0

		(tempC, tempF) = calc_temp(float(split_output[-1]) * 1000)

		with open(rawADCFileName, "a") as rawADCFile:

			rawADCFile.write("%0.4f," %(currTimeDelta))
			rawADCFile.write(",".join(split_output[0:10000]) + ",")
			rawADCFile.write(",".join(split_output[10000:10010]) + ",")
			rawADCFile.write(",".join(split_output[10010:10020]) + ",")
			rawADCFile.write("%03.2f" %(tempF))
			
			rawADCFile.write("\n")

		rawADCFile.close()

		newTime = datetime.datetime.now()
		newTimeDelta = (newTime - currTime).days * 86400 + (newTime - currTime).seconds + (newTime - currTime).microseconds / 1000000.0

		# print newTimeDelta, currTimeDelta, len(split_output)
		# print "rMic"



		# print len(timeData), len(audioData), len(doorData1), len(doorData2), tempData

		# while (i < (len(split_output) / 2 - 1)):
		# # every 1000th sample is from the door sensor
		# 	if (((i + 1) % 1001) == 1000):
	
				# with open(doorFileName, "a") as doorFile:
				# 	doorFile.write("{0:.2f},{1:.2f},{2:.2f}\n".format( float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 2]),float(split_output[2 * i + 3])))
				# doorFile.close()
		# 		sumD1 = sumD1 + float(split_output[2 * i + 1])
		# 		sumD2 = sumD2 + float(split_output[2 * i + 3])
		# 		kd = kd + 1

				
		# 		# with open(audioFileName, "a") as audioFile:
		# 		# 	audioFile.write("{0:.4f},{1:.2f}\n".format(float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1])))
		# 		# audioFile.close()
		# 		# sumA = sumA + float(split_output[2 * i + 1])
		# 		# ka = ka + 1

		# 		i = i + 2

		# 	else:	
		# 		# with open(audioFileName, "a") as audioFile:
		# 		# 	audioFile.write("{0:.4f},{1:.2f}\n".format(float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1])))
		# 		# audioFile.close()

		# 		######
		# 		# if ((i%100)==0):

		# 		# 	with open(audioFileName, "a") as audioFile:
		# 		# 		audioFile.write("{0:.4f},{1:.2f}\n".format(float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1])))
		# 		# 	audioFile.close()

		# 		sumA = sumA + float(split_output[2 * i + 1])
		# 		ka = ka + 1
		# 		i = i + 1
		
		
		# send 1 semple from the temperature sensor
		# try:
		# 	(tempC, tempF) = calc_temp(float(split_output[-1]) * 1000)
		# except:
		# 	sys.exit()

		# with open(tempFileName, "a") as tempFile:
		# 	tempFile.write("{0:0.4f},{1:03.2f},{2:0.4f}\n".format(float(split_output[-5]) + currTimeDelta, tempF, float(split_output[-5]) + currTimeDelta - testTime))
		# 	#tempFile.write("{0:0.4f},{1:03.2f},\n".format(float(split_output[-2]) + currTimeDelta, tempF))
		# tempFile.close()
		# sumAudio = sumAudio + (sumA/ka)
		# sumDoor1 = sumDoor1 + (sumD1/kd)
		# sumDoor2 = sumDoor2 + (sumD2/kd)
		# sumTemp = sumTemp + tempF

		testTime = float(split_output[-5]) + currTimeDelta


