from gpio_utils import *
from Constants import *
import rNTPTime
import socket
import time
import csv
import subprocess
import sys


# gets sensor values from the temperature sensor and the microphone, writes the data to a file and sends the data over a socket
def soundSense(startDateTime, hostIP, BASE_PORT, streaming = True, logging = True):

    server_address = (hostIP, BASE_PORT)
    # use custom function because datetime.strptime fails in multithreaded applications
    startTimeDT = rNTPTime.stripDateTime(startDateTime)
    audioFileName = BASE_PATH+"Relay_Station{0}/Audio/Audio{1}.txt".format(BASE_PORT, startTimeDT)
    doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)
    tempFileName = BASE_PATH+"Relay_Station{0}/Temperature/Temperature{1}.txt".format(BASE_PORT, startTimeDT)
    
    sensorMessage = " ADC "
    
    # write header information
    with open(audioFileName, "w") as audioFile:
        audioFile.write(startDateTime+"\n")
	audioFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
	audioFile.write("Timestamp,Ambient Noise Level\n")
    audioFile.close()
		
    with open(doorFileName, "w") as doorFile:
        doorFile.write(startDateTime+"\n")
	doorFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
	doorFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
    doorFile.close()
		
    with open(tempFileName, "w") as tempFile:
        tempFile.write(startDateTime+"\n")
	tempFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
	tempFile.write("Timestamp,Degree F\n")
    tempFile.close()
		
    # get starting time according to the BBB. This is only used for time deltas
    startTime = datetime.datetime.now()
	
    iterations = -1
    dummyvar = 0
	
    sumAudio = 0
    sumDoor1 = 0
    sumDoor2 = 0
    sumTemp = 0
    
    while True:
	
		if iterations >= FILE_LENGTH:
			# update BS and get current time every FILE_LENGTH iterations
			sumAudio = sumAudio/dummyvar
			sumDoor1 = sumDoor1/dummyvar
			sumDoor2 = sumDoor2/dummyvar
			sumTemp = sumTemp/dummyvar
			startDateTime = rNTPTime.sendUpdate(server_address, iterations, sensorMessage, sumAudio, sumDoor1,sumDoor2, sumTemp, 5)
			iterations = -1
			sumAudio = 0
			sumDoor1 = 0
			sumDoor2 = 0
			sumTemp = 0
			dummyvar = 0
    
			
			# if startDateTime == None, the update failed, so we keep writing to the old file
			if startDateTime != None:
				startTimeDT = rNTPTime.stripDateTime(startDateTime)
				audioFile.close()
				doorFile.close()
				tempFile.close()
			
				audioFileName = BASE_PATH+"Relay_Station{0}/Audio/Audio{1}.txt".format(BASE_PORT, startTimeDT)
				doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)
				tempFileName = BASE_PATH+"Relay_Station{0}/Temperature/Temperature{1}.txt".format(BASE_PORT, startTimeDT)
			
				with open(audioFileName, "w") as audioFile:
					audioFile.write(startDateTime+"\n")
					audioFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					audioFile.write("Timestamp,Ambient Noise Level\n")
                                audioFile.close()		
				with open(doorFileName, "w") as doorFile:
					doorFile.write(startDateTime+"\n")
					doorFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					doorFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
				doorFile.close()
				with open(tempFileName, "w") as tempFile:
					tempFile.write(startDateTime+"\n")
					tempFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					tempFile.write("Timestamp,Degree F\n")
                                tempFile.close()
				# get new local start time
				startTime = datetime.datetime.now()

		# update BS every UPDATE_LENGTH iterations
		elif (iterations % UPDATE_LENGTH) == (UPDATE_LENGTH - 2):
			sumAudio = sumAudio/UPDATE_LENGTH
			sumDoor1 = sumDoor1/UPDATE_LENGTH
			sumDoor2 = sumDoor2/UPDATE_LENGTH
			sumTemp = sumTemp/UPDATE_LENGTH
			rNTPTime.sendUpdate(server_address, iterations, sensorMessage, sumAudio, sumDoor1, sumDoor2, sumTemp, 5)	
			sumAudio = 0
			sumDoor1 = 0
			sumDoor2 = 0
			sumTemp = 0
			dummyvar = 0

		iterations += 1
		dummyvar += 1
		
		# calculate the time since the start of the data collection
		currTime = datetime.datetime.now()
		currTimeDelta = (currTime - startTime).days * 86400 + (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
			
		# run the c code to get one second of data from the ADC
		proc = subprocess.Popen(["./root/besi-relay-station/BESI_LOGGING_R/ADC1"], stdout=subprocess.PIPE,)
		# anything printed in ADC.c is captured in output
		output = proc.communicate()[0]
		split_output = output.split(',')
			
		# data is in <timestamp>,<value> format
		# 100 samples/second from the mic and 1 sample/sec from the temperature sensor
		i = 0 
		ka = 0
		sumA = 0
		kd = 0
		sumD1 = 0
		sumD2 = 0
		while (i < (len(split_output) / 2 - 1)):
		# every 11th sample is from the door sensor
			if (((i + 1) % 12) == 11):
				#doorFile.write(struct.pack("fff", float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1]),float(split_output[2 * i + 3])) + "~~")
				with open(doorFileName, "a") as doorFile:
				    doorFile.write("{0:.2f},{1:.2f},{2:.2f}\n".format( float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1]),float(split_output[2 * i + 3])))
				doorFile.close()
                                sumD1 = sumD1 + float(split_output[2 * i + 1])
				sumD2 = sumD2 + float(split_output[2 * i + 3])
				kd = kd + 1
				i = i + 2

			else:		
				#audioFile.write(struct.pack("ff", float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1])) + "~~")
				with open(audioFileName, "a") as audioFile:
				    audioFile.write("{0:.2f},{1:.2f}\n".format(float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1])))
                                audioFile.close()
				sumA = sumA + float(split_output[2 * i + 1])
				ka = ka + 1
				i = i + 1
		
		
		# send 1 semple from the temperature sensor
		try:
			(tempC, tempF) = calc_temp(float(split_output[-1]) * 1000)
		except:
			sys.exit()

		with open(tempFileName, "a") as tempFile:
		    tempFile.write("{0:0.4f},{1:03.2f},\n".format(float(split_output[-2]) + currTimeDelta, tempF))
		tempFile.close()
		sumAudio = sumAudio + (sumA/ka)
		sumDoor1 = sumDoor1 + (sumD1/kd)
		sumDoor2 = sumDoor2 + (sumD2/kd)
		sumTemp = sumTemp + tempF

