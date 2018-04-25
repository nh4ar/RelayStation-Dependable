from gpio_utils import *
from Constants import *
import rNTPTime
import socket
import time
import csv
import subprocess
import sys
from pyAudioAnalysis import audioFeatureExtraction
import rawADC
import os

def audioFeatureExt(startDateTime, hostIP, BASE_PORT):

	time.sleep((LOOP_DELAY * UPDATE_DELAY))

	#Heartbeat stuff
	server_address = (hostIP, BASE_PORT)
	audioMessage = []
	sumAudio = 0
	sumAudioFeat = 0
	iterations = 0

	startLine = 3 #from rawADC - line0 = header, line1 = time, line2 = description
	aSamplingFreq = 10000
	winSize = 0.250 #sec
	winStep = 0.125 #sec

	audioBuffer = ["0"]

	startTimeDT = rNTPTime.stripDateTime(startDateTime)
	audioFeatureFileName = BASE_PATH+"Relay_Station{0}/AudioF/AudioF{1}.txt".format(BASE_PORT, startTimeDT)

	#for HEARTBEAT_LOG
	audioHeartbeatFileName = BASE_PATH+"Relay_Station{0}/heartbeatLog/Audio.txt".format(BASE_PORT)
	with open(audioHeartbeatFileName, "a") as audioHeartbeat:
		audioHeartbeat.write("sensorType, timeStamp, value\n")
	#for HEARTBEAT_LOG

	with open(audioFeatureFileName, "w") as audioFeatureFile:
		audioFeatureFile.write(startDateTime+"\n")
		audioFeatureFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
		audioFeatureFile.write("Timestamp, ZCR, Energy, Energy Entropy, Spectral Centroid, Spectral Spread, Spectral Entropy, Spectral Flux, Spectral Rolloff, MFCC0, MFCC1, MFCC2, MFCC3, MFCC4, MFCC5, MFCC6, MFCC7, MFCC8, MFCC9, MFCC10, MFCC11, MFCC12, ChromaVector1, , ChromaVector2, ChromaVector3, ChromaVector4, ChromaVector5, ChromaVector6, ChromaVector7, ChromaVector8, ChromaVector9, ChromaVector10, ChromaVector11, ChromaVector12, ChromaDeviation\n")
		#audioFeatureFile.write("Timestamp, ZCR, Energy, Energy Entropy, Spectral Centroid, Spectral Spread, Spectral Entropy, Spectral Flux, Spectral Rolloff, MFCC0, MFCC1, MFCC2, MFCC3, MFCC4, MFCC5, MFCC6, MFCC7, MFCC8, MFCC9, MFCC10, MFCC11, MFCC12, ChromaVector1, , ChromaVector2, ChromaVector3, ChromaVector4, ChromaVector5, ChromaVector6, ChromaVector7, ChromaVector8, ChromaVector9, ChromaVector10, ChromaVector11, ChromaVector12, ChromaDeviation\n")
	audioFeatureFile.close()

	currLine = startLine #current line to read/write from

	while True:

		startTimeDT = rNTPTime.stripDateTime(startDateTime)
		rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)

		rawlineCount = 0
		for line in open(rawADCFileName).xreadlines(  ): rawlineCount += 1
		# close(rawADCFileName)

		# print "2017-08-07 %d%d:%d%d:%d%d.000" %(1,1,1,1,1,1)
		# if startTimeDT != rawADC_Time:
		# 	print "FileChanged!!!!

		# print "rawADC Size = ", rawlineCount, ", AudioFeature Size = ",currLine, ", rawADCTime = ", rawADC.rawADC_Time, ", AudioFileTime = ", startTimeDT

		if rawlineCount > currLine:
			with open(rawADCFileName, "r") as rawADCFile:
				rawADC_string = rawADCFile.readlines()[currLine]
			# rawADCFile.close()

			rawADC_Data = rawADC_string.split(',')

			timeDelta = float(rawADC_Data[0])
			# audioData = rawADC_Data[1:10001]
			# doorData1 = rawADC_Data[10001:10011]
			# doorData2 = rawADC_Data[10011:10021]
			# tempF = float(rawADC_Data[-1])

			if len(rawADC_Data[1:10001]) == 10000:
				# audioFeatureExtraction.stFeatureExtraction(data, Fs, window, step)
				# F = audioFeatureExtraction.stFeatureExtraction(rawADC_Data[1:10001], aSamplingFreq,
				#  winSize*aSamplingFreq, winStep*aSamplingFreq)

				if len(audioBuffer) >= 1250: #
					F = audioFeatureExtraction.stFeatureExtraction(audioBuffer+rawADC_Data[1:10001], aSamplingFreq,
						winSize*aSamplingFreq, winStep*aSamplingFreq)
					timeDelta = timeDelta-0.125
				else: #no audio buffer - first run - just create a new file
					F = audioFeatureExtraction.stFeatureExtraction(rawADC_Data[1:10001], aSamplingFreq,
						winSize*aSamplingFreq, winStep*aSamplingFreq)

				audioBuffer = rawADC_Data[8751:10001]
				
				with open(audioFeatureFileName, "a") as audioFeatureFile:

					for i in range(0, 7):
						timeStepDelta = winStep*i
						audioFeatureFile.write("%0.4f," %(timeDelta+timeStepDelta))
						audioFeatureFile.write("%f," %(F[0,i]))
						audioFeatureFile.write("%f," %(F[1,i]))
						audioFeatureFile.write("%f," %(F[2,i]))
						audioFeatureFile.write("%f," %(F[3,i]))
						audioFeatureFile.write("%f," %(F[4,i]))
						audioFeatureFile.write("%f," %(F[5,i]))
						audioFeatureFile.write("%f," %(F[6,i]))
						audioFeatureFile.write("%f," %(F[7,i]))
						audioFeatureFile.write("%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f,"
							%(F[8,i], F[9,i], F[10,i], F[11,i], F[12,i], F[13,i], F[14,i], F[15,i],
							 F[16,i], F[17,i], F[18,i], F[19,i], F[20,i]))
						audioFeatureFile.write("%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f,"
							%(F[21,i], F[22,i], F[23,i], F[24,i], F[25,i], F[26,i], F[27,i], F[28,i],
							 F[29,i], F[30,i], F[31,i], F[32,i]))
						audioFeatureFile.write("%f\n" %(F[33,i]))	

						sumAudio += float(F[2,i]) #data for HEART BEAT
						sumAudioFeat += float(F[3,i])

				audioFeatureFile.close()			

				sumAudio = sumAudio/7 # there's 7 windows in 1 sec
				sumAudioFeat = sumAudioFeat/7
				iterations += 1

				currLine = currLine + 1 #move to the next Audio line


		#if finish audioFeature Ext + rawADC creates a new file
		elif rawADC.rawADC_Time != startTimeDT:

			rawlineCount = 0
			for line in open(rawADCFileName).xreadlines(  ): rawlineCount += 1

			if rawlineCount==currLine:

				#delete the previous rawADCFile
				try:
					time.sleep(5) #wait for the Door thread to finish
					os.remove(rawADCFileName)
				except :
					pass

				startDateTime = rawADC.rawADC_startDateTime
				startTimeDT = str(rawADC.rawADC_Time)
				audioFeatureFileName = BASE_PATH+"Relay_Station{0}/AudioF/AudioF{1}.txt".format(BASE_PORT, startTimeDT)

				# create new audioFeatureFile
				with open(audioFeatureFileName, "w") as audioFeatureFile:
					audioFeatureFile.write(startDateTime+"\n")
					audioFeatureFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					audioFeatureFile.write("Timestamp, ZCR, Energy, Energy Entropy, Spectral Centroid, Spectral Spread, Spectral Entropy, Spectral Flux, Spectral Rolloff, MFCC0, MFCC1, MFCC2, MFCC3, MFCC4, MFCC5, MFCC6, MFCC7, MFCC8, MFCC9, MFCC10, MFCC11, MFCC12, ChromaVector1, , ChromaVector2, ChromaVector3, ChromaVector4, ChromaVector5, ChromaVector6, ChromaVector7, ChromaVector8, ChromaVector9, ChromaVector10, ChromaVector11, ChromaVector12, ChromaDeviation\n")
				audioFeatureFile.close()
				currLine = startLine
				# print "new File Created"

				#update new rawADC filename to open
				rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)

		if iterations>=UPDATE_LENGTH:
			sumAudio = sumAudio/iterations
			iterations = 0
			audioMessage = []
			audioMessage.append("Audio")
			audioMessage.append(str("{0:.3f}".format(sumAudio))) #Energy
			audioMessage.append(str("{0:.3f}".format(sumAudioFeat))) #Teager
			tempDateTime = rNTPTime.sendUpdate(server_address, audioMessage, 5) #Audio uses startDateTime from rawADC
			sumAudio = 0
			sumAudioFeat = 0

			#for HEARTBEAT_LOG
			with open(audioHeartbeatFileName, "a") as audioHeartbeat:
				audioHeartbeat.write("Audio,{0},{1}\n".format(tempDateTime,audioMessage[1]))
				# audioHeartbeat.write("sensorType, timeStamp, value\n")
			#for HEARTBEAT_LOG

		
	# END WHILE LOOP
