from gpio_utils import *
from Constants import *
import rNTPTime
import socket
import time
import csv
import subprocess
import sys
import rawADC
import numpy
from scipy import ndimage

def doorSensor(startDateTime, hostIP, BASE_PORT):

	time.sleep((LOOP_DELAY * UPDATE_DELAY))

	#Heartbeat stuff
	server_address = (hostIP, BASE_PORT)
	doorMessage = []
	tempMessage = []
	sumDoor1 = 0
	sumDoor2 = 0
	sumTemp = 0
	iterations = 0

	startLine = 3 # 3 lines description in the beginning
	currLine = startLine #current line to read/write from

	startTimeDT = rNTPTime.stripDateTime(startDateTime)

	doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)
	with open(doorFileName, "w") as doorFile:
		doorFile.write(startDateTime+"\n")
		doorFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
		doorFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
	doorFile.close()
		
	tempFileName = BASE_PATH+"Relay_Station{0}/Temperature/Temperature{1}.txt".format(BASE_PORT, startTimeDT)
	with open(tempFileName, "w") as tempFile:
		tempFile.write(startDateTime+"\n")
		tempFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
		tempFile.write("Timestamp,Degree F\n")
	tempFile.close()

	# for testing doorway crossing event
	directionFileName = BASE_PATH+"Relay_Station{0}/Direction/Direction{1}.txt".format(BASE_PORT, startTimeDT)
	with open(directionFileName, "w") as directionFile:
		directionFile.write(startDateTime+"\n")
		directionFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
		directionFile.write("Timestamp,Direction\n")
	directionFile.close()

	#for HEARTBEAT_LOG
	tempHeartbeatFileName = BASE_PATH+"Relay_Station{0}/heartbeatLog/Temperature.txt".format(BASE_PORT)
	with open(tempHeartbeatFileName, "a") as tempHeartbeat:
		tempHeartbeat.write("sensorType, timeStamp, value\n")
	#for HEARTBEAT_LOG

	while True:

		startTimeDT = rNTPTime.stripDateTime(startDateTime)
		rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)
		# doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)

		rawlineCount = 0
		for line in open(rawADCFileName).xreadlines(  ): rawlineCount += 1

		if rawlineCount > currLine:
			with open(rawADCFileName, "r") as rawADCFile:
				rawADC_string = rawADCFile.readlines()[currLine]

			rawADC_Data = rawADC_string.split(',')
			timeDelta = float(rawADC_Data[0])

			# print float(rawADC_Data[-1]), " length=", len(rawADC_Data[10000:10021])

			# if len(rawADC_Data[-1]) == 1:
			# 	with open(tempFileName, "a") as tempFile:
			# 		tempFile.write("%0.2f," %( timeDelta ))
			# 		tempFile.write("%03.2f\n" %( float(rawADC_Data[-1])))

			if len(rawADC_Data[10001:10022]) == 21: #20(Doors) + 1(Temp)

				#Door sensor data processing
				rawDoorData = map(float,rawADC_Data[10001:10021])
				rawDoorData = numpy.array(rawDoorData)

				doorData = doorProcessing(timeDelta, rawDoorData)
				
				#END Door sensor data processing

				with open(doorFileName, "a") as doorFile:
					for i in range(0,10):
						doorFile.write("%0.2f," %( timeDelta + (0.1*i) ))
						doorFile.write("%d," %( doorData[i]))
						doorFile.write("%d\n" %( doorData[i+10]))
				doorFile.close()
						
				with open(tempFileName, "a") as tempFile:
					tempFile.write("%0.2f," %( timeDelta ))
					tempFile.write("%03.2f\n" %( float(rawADC_Data[-1])))
				tempFile.close()

				#value for heartbeat
				sumDoor1 += numpy.mean(doorData[0:10])
				sumDoor1 += numpy.mean(doorData[10:20])
				sumTemp += float(rawADC_Data[-1])
				iterations += 1
				

				currLine = currLine + 1 #move to the next Audio line



		#if finish audioFeature Ext + rawADC creates a new file
		elif rawADC.rawADC_Time != startTimeDT:

			rawlineCount = 0
			for line in open(rawADCFileName).xreadlines(  ): rawlineCount += 1

			if rawlineCount==currLine:

				startDateTime = rawADC.rawADC_startDateTime
				startTimeDT = str(rawADC.rawADC_Time)
				doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)

				# create new door file
				with open(doorFileName, "w") as doorFile:
					doorFile.write(startDateTime+"\n")
					doorFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					doorFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
				doorFile.close()

				currLine = startLine
				# print "new File Created"

				tempFileName = BASE_PATH+"Relay_Station{0}/Temperature/Temperature{1}.txt".format(BASE_PORT, startTimeDT)
				with open(tempFileName, "w") as tempFile:
					tempFile.write(startDateTime+"\n")
					tempFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					tempFile.write("Timestamp,Degree F\n")
				tempFile.close()

				directionFileName = BASE_PATH+"Relay_Station{0}/Direction/Direction{1}.txt".format(BASE_PORT, startTimeDT)
				with open(directionFileName, "w") as directionFile:
					directionFile.write(startDateTime+"\n")
					directionFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					directionFile.write("Timestamp,Direction\n")
				directionFile.close()

				#update new rawADC filename to open
				rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)


		if iterations>=UPDATE_LENGTH: #HEARTBEAT
			sumDoor1 = sumDoor1/iterations
			sumDoor2 = sumDoor2/iterations
			sumTemp = sumTemp/iterations
			iterations = 0
			doorMessage = []
			doorMessage.append("Door")
			doorMessage.append(str("{0:.3f}".format(sumDoor1)))
			doorMessage.append(str("{0:.3f}".format(sumDoor2)))
			tempDateTime = rNTPTime.sendUpdate(server_address, doorMessage, 5) #Audio uses startDateTime from rawADC
			sumAudio = 0

			tempMessage = []
			tempMessage.append("Temperature")
			tempMessage.append(str("{0:.3f}".format(sumTemp)))
			tempDateTime = rNTPTime.sendUpdate(server_address, tempMessage, 5) #uses startDateTime from rawADC
			sumTemp = 0

			#for HEARTBEAT_LOG
			with open(tempHeartbeatFileName, "a") as tempHeartbeat:
				tempHeartbeat.write("Temperature,{0},{1}\n".format(tempDateTime,tempMessage[1]))
			#for HEARTBEAT_LOG


		#END while True



def doorProcessing(timeDelta, rawDoorData):

	direction = 0

	doorData = rawDoorData
	# print 'CH1: ', doorData[0:10], 'CH2: ', doorData[10:20]
	doorData[doorData>0.3] = 1
	doorData[doorData<0.7] = 0
	doorData = map(int,doorData)

	# print doorData

	# doorCH1 = doorData[0:10]
	# doorCH2 = doorData[10:20]

	# # print 'CH1: ', doorCH1, 'CH2: ', doorCH2 

	# for i in range(1,len(doorCH1)): 

	# 	if direction == 0: # no direction detected yet
	# 		if ( doorCH1[i] - doorCH1[i-1] ) == 1: # if ch1 is up
	# 			if doorCH2[i] == 0: #ch1 up but not ch2
	# 				for j in range(i+1,len(doorCH2)): #check next samples of ch2 
	# 					if doorCH2[j] == 1:
	# 						direction = 1
	# 						break

	# 			else:
	# 				direction = -1
	# 	else: # if direction is detected -> end the loop
	# 		break

	# # PRINT DIRECTION
	# if direction == 1:
	# 	print "\n"
	# 	print "Move to ROOM #2"
	# 	print "\n"

	# if direction == -1:
	# 	print "\n"
	# 	print "Move to ROOM #1"
	# 	print "\n"

	# if direction != 0: # there's a doorway event

	# 	with open(directionFileName, "a") as directionFile:
	# 		directionFile.write("%0.2f," %( timeDelta ))
	# 		directionFile.write("%d\n" %( direction))
	# 	directionFile.close()


	return doorData


