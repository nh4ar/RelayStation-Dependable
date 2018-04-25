#code to interface with the TSL2561 ambient light sensor over i2c
# continuously samples lux semsor and writes result to given can write
from gpio_utils import *
from Constants import *
import rNTPTime
import time
import csv
import struct
import sys
import socket

global agiType
global agiIndx
global agiStatus

agiType = 0
agiIndx = 0
agiStatus = False

def lightSense(startDateTime, hostIP, BASE_PORT,  streaming=True, logging=True):

    global agiType
    global agiIndx
    global agiStatus

    server_address = (hostIP, BASE_PORT)
    startTimeDT = rNTPTime.stripDateTime(startDateTime)
    lightFileName = BASE_PATH+"Relay_Station{0}/Light/Light{1}.txt".format(BASE_PORT, startTimeDT)
    lightMessage = []
    
    light_i2c = i2c_light_init(LIGHT_ADDR)
        
    with open(lightFileName, "w") as lightFile:
        lightFile.write(startDateTime+"\n")
        lightFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
        lightFile.write("Timestamp,Lux\n")
	
    startTime = datetime.datetime.now()
    iterations = -1
    sumLux = 0
    dummyvar = 0

    #for HEARTBEAT_LOG
    lightHeartbeatFileName = BASE_PATH+"Relay_Station{0}/heartbeatLog/Light.txt".format(BASE_PORT)
    with open(lightHeartbeatFileName, "a") as lightHeartbeat:
        lightHeartbeat.write("sensorType, timeStamp, value\n")
    #for HEARTBEAT_LOG

    while True:
        if iterations >= FILE_LENGTH:
            sumLux = sumLux/dummyvar

            lightMessage = []
            lightMessage.append("Light")
            lightMessage.append(str("{0:.3f}".format(sumLux)))

            startDateTime = rNTPTime.sendUpdate(server_address, lightMessage, 5)

            #agiIndx = update[0]
            #agiType = update[1]
            #if agiType!=0:
            #    agiStatus = True
            #else:
            #    agiStatus = False
            #startDateTime = update[2]

            #startDateTime = rNTPTime.sendUpdate(server_address, iterations, sensorMessage, sumLux, 0, 0, 0, 5) 
            # " light samples"
            iterations = -1
            sumLux = 0
            dummyvar = 0
				
            if startDateTime != None:
                startTimeDT = rNTPTime.stripDateTime(startDateTime)
                #startTimeDT = datetime.datetime.now()
			
                lightFileName = BASE_PATH+"Relay_Station{0}/Light/Light{1}.txt".format(BASE_PORT, startTimeDT)
                with open(lightFileName, "w") as lightFile:
                    lightFile.write(startDateTime+"\n")
                    lightFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
                    lightFile.write("Timestamp,Lux\n")

                startTime = datetime.datetime.now()
		
        elif (iterations % UPDATE_LENGTH) == (UPDATE_LENGTH - 2):
            sumLux = sumLux/UPDATE_LENGTH
            
            lightMessage = []
            lightMessage.append("Light")
            lightMessage.append(str("{0:.3f}".format(sumLux)))
            startDateTime = rNTPTime.sendUpdate(server_address, lightMessage, 5)

            #agiIndx = update[0]
            #agiType = update[1]
            #if agiType!=0:
            #    agiStatus = True
            #else:
            #    agiStatus = False
            #startDateTime = update[2]


            #rNTPTime.sendUpdate(server_address, iterations, sensorMessage, sumLux, 0,0,0, 5) # " light samples"
            sumLux = 0
            dummyvar = 0

            #for HEARTBEAT_LOG
            with open(lightHeartbeatFileName, "a") as lightHeartbeat:
                lightHeartbeat.write("Light,{0},{1}\n".format(startDateTime,lightMessage[1]))
            #for HEARTBEAT_LOG


        iterations += 1
        dummyvar += 1

        # calculate time since start
        currTime = datetime.datetime.now()
        currTimeDelta = (currTime - startTime).days * 86400 + (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
        # read light sensor
        # error reading i2c bus. Try to reinitialize sensor
        lightLevel = lux_calc(light_i2c.readU16(LIGHT_REG_LOW), light_i2c.readU16(LIGHT_REG_HIGH))
        if lightLevel == -1:
            light_i2c = i2c_light_init(LIGHT_ADDR)
		
        #if logging:      
             #lightWriter.writerow(("{0:.2f}".format(currTimeDelta), "{0:.2f}".format(lightLevel)))
			
        with open(lightFileName, "a") as lightFile:
            lightFile.write("{0:.2f},{1:.2f},\n".format(currTimeDelta, lightLevel))

        sumLux = sumLux + lightLevel
        time.sleep(LOOP_DELAY * UPDATE_DELAY)

