
import numpy
import os
import shutil
import datetime
import time
import rNTPTime
from Constants import *

def motionFeatExt(startDateTime, hostIP, BASE_PORT, pebbleFolder):

	x=[]
	y=[]
	z=[]
	max_x_values=[]
	min_x_values=[]
	mean_x_values=[]
	max_y_values=[]
	min_y_values=[]
	mean_y_values=[]
	max_z_values=[]
	min_z_values=[]
	mean_z_values=[]

	iterations = 0
	HB_Pixie_Value = 0

	server_address = (hostIP, BASE_PORT)

	#Fs = 50.0;  # sampling rate
	#Ts = 1.0/Fs; # sampling interval
	#t = numpy.arange(0,1,Ts) # time vector

	while True:

		# f = open('C:\Users\jah4yq\Downloads\pebble_data_1504247643122.csv',"r")
		#f = open('C:\Users\jah4yq\Downloads\pebble_data_1504251277808.csv',"r")
		#f = open('/media/card/r101.csv',"r")
		# Get file name to open
		files = os.walk(BASE_PATH + pebbleFolder + "/").next()[2] #BASE_PATH = /media/card/
		files.sort() #previous file first
		if (len(files) >= 2) :#need more than 2 files -> previous one is finished recording pebble data
			
			print "reading Motion from " + files[0]
			f = open(BASE_PATH + pebbleFolder + "/" + files[0], "r") #f = open('/media/card/pebble_data_XXXXXX.csv',"r")
			rawlineCount = 0
			for numLines in f.xreadlines(  ): rawlineCount += 1 # read #of lines
			f.close()

			f = open(BASE_PATH + pebbleFolder + "/" + files[0], "r")
			line = f.readline()	#line pointer at the first line: "z,y,x,offset,timestamp"
			for q in range(rawlineCount):
				line = f.readline() # line pointer at the first DATA line
				count = 1
				#print line
				num = line.split(',')
				# print num
				# print num[0]
				if len(num) >= 5:
					z.append(int(num[0]))
					y.append(int(num[1]))
					x.append(int(num[2]))
				# for i in line.split(','):
				# 	#print i, 
				# 	try:
				# 		num = int(i)
				# 		if count==1:
				# 			z.append(num)
				# 		elif count==2:
				# 			y.append(num)
				# 		elif count==3:
				# 			x.append(num)
				# 		count += 1
				# 	except:
				# 		print "err converting num = int(i)"
					
			f.close()
			#finished reading all lines

			x.append(0)
			y.append(0)
			z.append(0)

			#Generate destination file
			#Convert Epoch time -> readable Time 
			dstFileTime = files[0].split('_')
			dstFileTime = dstFileTime[2].split('.')
			dstFileTime = datetime.datetime.fromtimestamp(int(dstFileTime[0])/1000).strftime('%y-%m-%d_%H-%M-%S')

			PebbleFeatureFileName = BASE_PATH+"Relay_Station{0}/PebbleFeature/PebbleFeature{1}.txt".format(BASE_PORT, dstFileTime)
			with open(PebbleFeatureFileName, "w") as PebbleFeatureFile:
				PebbleFeatureFile.write(dstFileTime+"\n")
				PebbleFeatureFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
				PebbleFeatureFile.write("x_max,x_min,x_mean,x_std,x_fft_mean,x_fft_0_1_max,x_fft_1_3_max,x_fft_3_10_max,x_teager_mean,x_teager_max,y_max,y_min,y_mean,y_std,y_fft_mean,y_fft_0_1_max,y_fft_1_3_max,y_fft_3_10_max,y_teager_mean,y_teager_max,z_max,z_min,z_mean,z_std,z_fft_mean,z_fft_0_1_max,z_fft_1_3_max,z_fft_3_10_max,z_teager_mean,z_teager_max\n ")
			# PebbleFeatureFile.close()

			# f = open('C:\Users\jah4yq\Downloads\pebble_data_accel_features.csv',"w")
			# f.write(str("x_max") + ", " +str("x_min") + ", " + str("x_mean") + ", " + str("x_std") + ", " + str("x_fft_mean") + ", " + str("x_fft_0_1_max") + ", " + str("x_fft_1_3_max") + ", " + str("x_fft_3_10_max") + ", " + str("x_teager_mean") + ", " + str("x_teager_max") + ", " +  str("y_max") + ", " +str("y_min") + ", " + str("y_mean") + ", " + str("y_std") + ", " + str("y_fft_mean") + ", " + str("y_fft_0_1_max") + ", " + str("y_fft_1_3_max") + ", " + str("y_fft_3_10_max") + ", " + str("y_teager_mean") + ", " + str("y_teager_max") + ", " + str("z_max") + ", " + str("z_min") + ", " + str("z_mean") + ", " + str("z_std") + ", " + str("z_fft_mean") + ", " + str("z_fft_0_1_max") + ", " + str("z_fft_1_3_max") + ", " + str("z_fft_3_10_max") + ", " + str("z_teager_mean") + ", " + str("z_teager_max") + "\n ")

			for m in range(rawlineCount/1500-1):
				lower_lim = 1500*m
				upper_lim = 1500*m+2999	
				
				
				
				x_max = max(x[lower_lim:upper_lim])
				x_min = min(x[lower_lim:upper_lim])
				x_mean = numpy.mean(x[lower_lim:upper_lim])
				x_std = numpy.std(x[lower_lim:upper_lim], ddof=1)
				
				Fs = 50.0;  # sampling rate
				Ts = 1.0/Fs; # sampling interval
				t = numpy.arange(0,1,Ts) # time vector
				n = 3000 # length of the signal
				k = numpy.arange(n)
				T = n/Fs
				frq = k/T # two sides frequency range
				frq = frq[range(n/2)] # one side frequency range
				
				X = numpy.fft.fft(x[lower_lim:upper_lim])/n # fft computing and normalization
				X = X[range(n/2)]
				X = numpy.absolute(X)
				X = list(X)
				
				i1 = X.index(max(numpy.absolute(X[1:60]))) #finds the index of the max fft magnitude between 0&1 Hz
				i2 = X.index(max(numpy.absolute(X[61:180]))) #finds the index of the max fft magnitude between 1&3 Hz
				i3 = X.index(max(numpy.absolute(X[181:600]))) #finds the index of the max fft magnitude between 3&10 Hz
				
				x_fft_0_1_max = frq[i1] 
				x_fft_1_3_max = frq[i2]
				x_fft_3_10_max = frq[i3]
				
				X_sum = sum(X)
				X_mag = sum(numpy.multiply(X,frq))
				x_fft_mean = X_sum/X_mag


				
				y_max = max(y[lower_lim:upper_lim])
				y_min = min(y[lower_lim:upper_lim])
				y_mean = numpy.mean(y[lower_lim:upper_lim])
				y_std = numpy.std(y[lower_lim:upper_lim], ddof=1)
				
				Y = numpy.fft.fft(y[lower_lim:upper_lim])/n # fft computing and normalization
				Y = Y[range(n/2)]
				Y = numpy.absolute(Y)
				Y = list(Y)
				
				i1 = Y.index(max(numpy.absolute(Y[1:60]))) #finds the index of the max fft magnitude between 0&1 Hz
				i2 = Y.index(max(numpy.absolute(Y[61:180]))) #finds the index of the max fft magnitude between 1&3 Hz
				i3 = Y.index(max(numpy.absolute(Y[181:600]))) #finds the index of the max fft magnitude between 3&10 Hz
				
				y_fft_0_1_max = frq[i1] 
				y_fft_1_3_max = frq[i2]
				y_fft_3_10_max = frq[i3]
				
				Y_sum = sum(Y)
				Y_mag = sum(numpy.multiply(Y,frq))
				y_fft_mean = Y_sum/Y_mag
				
				
				
				z_max = max(z[lower_lim:upper_lim])
				z_min = min(z[lower_lim:upper_lim])
				z_mean = numpy.mean(z[lower_lim:upper_lim])
				z_std = numpy.std(z[lower_lim:upper_lim], ddof=1)
				
				Z = numpy.fft.fft(z[lower_lim:upper_lim])/n # fft computing and normalization
				Z = Z[range(n/2)]
				Z = numpy.absolute(Z)
				Z = list(Z)
				
				i1 = Z.index(max(numpy.absolute(Z[1:60]))) #finds the index of the max fft magnitude between 0&1 Hz
				i2 = Z.index(max(numpy.absolute(Z[61:180]))) #finds the index of the max fft magnitude between 1&3 Hz
				i3 = Z.index(max(numpy.absolute(Z[181:600]))) #finds the index of the max fft magnitude between 3&10 Hz
				
				z_fft_0_1_max = frq[i1] 
				z_fft_1_3_max = frq[i2]
				z_fft_3_10_max = frq[i3]
				
				Z_sum = sum(Z)
				Z_mag = sum(numpy.multiply(Z,frq))
				z_fft_mean = Z_sum/Z_mag
				
				x_teager = []
				y_teager = []
				z_teager = []
				
				for g in range(3000):
					if g==0:
						xx=(x[g+lower_lim])^2
						yy=(y[g+lower_lim])^2
						zz=(z[g+lower_lim])^2
					elif g != 0:
						xx = (x[g+lower_lim])^2 - (x[g+lower_lim-1])*(x[g+lower_lim+1])
						yy = (y[g+lower_lim])^2 - (y[g+lower_lim-1])*(y[g+lower_lim+1])
						zz = (z[g+lower_lim])^2 - (z[g+lower_lim-1])*(z[g+lower_lim+1])
						#xx=(x[g+lower_lim])^2
						#yy=(y[g+lower_lim])^2
						#zz=(z[g+lower_lim])^2
					x_teager.append(xx)
					y_teager.append(yy)
					z_teager.append(zz)
					
				x_teager_max = max(x_teager)
				x_teager_mean = numpy.mean(x_teager)
				y_teager_max = max(y_teager)
				y_teager_mean = numpy.mean(y_teager)	
				z_teager_max = max(z_teager)
				z_teager_mean = numpy.mean(z_teager)
				
				
				HB_Pixie_Value = x_max

				# f.write(str(x_max) + ", " +str(x_min) + ", " + str(x_mean) + ", " + str(x_std) + ", " + str(x_fft_mean) + ", " + str(x_fft_0_1_max) + ", " + str(x_fft_1_3_max) + ", " + str(x_fft_3_10_max) + ", " + str(x_teager_mean) + ", " + str(x_teager_max) + ", " +  str(y_max) + ", " +str(y_min) + ", " + str(y_mean) + ", " + str(y_std) + ", " + str(y_fft_mean) + ", " + str(y_fft_0_1_max) + ", " + str(y_fft_1_3_max) + ", " + str(y_fft_3_10_max) + ", " + str(y_teager_mean) + ", " + str(y_teager_max) + ", " + str(z_max) + ", " + str(z_min) + ", " + str(z_mean) + ", " + str(z_std) + ", " + str(z_fft_mean) + ", " + str(z_fft_0_1_max) + ", " + str(z_fft_1_3_max) + ", " + str(z_fft_3_10_max) + ", " + str(z_teager_mean) + ", " + str(z_teager_max) + "\n ")
				with open(PebbleFeatureFileName, "a") as PebbleFeatureFile:
					PebbleFeatureFile.write(str(x_max) + ", " +str(x_min) + ", " + str(x_mean) + ", " + str(x_std) + ", " + str(x_fft_mean) + ", " + str(x_fft_0_1_max) + ", " + str(x_fft_1_3_max) + ", " + str(x_fft_3_10_max) + ", " + str(x_teager_mean) + ", " + str(x_teager_max) + ", " +  str(y_max) + ", " +str(y_min) + ", " + str(y_mean) + ", " + str(y_std) + ", " + str(y_fft_mean) + ", " + str(y_fft_0_1_max) + ", " + str(y_fft_1_3_max) + ", " + str(y_fft_3_10_max) + ", " + str(y_teager_mean) + ", " + str(y_teager_max) + ", " + str(z_max) + ", " + str(z_min) + ", " + str(z_mean) + ", " + str(z_std) + ", " + str(z_fft_mean) + ", " + str(z_fft_0_1_max) + ", " + str(z_fft_1_3_max) + ", " + str(z_fft_3_10_max) + ", " + str(z_teager_mean) + ", " + str(z_teager_max) + "\n ")


			files = os.walk(BASE_PATH + pebbleFolder + "/").next()[2] #BASE_PATH = /media/card/
			files.sort() #previous file first
			if (len(files) >= 2) :#need more than 2 files -> previous one is finished recording pebble data
				f = open(BASE_PATH + pebbleFolder + "/" + files[0], "r") #f = open('/media/card/pebble_data_XXXXXX.csv',"r")
			src = BASE_PATH + pebbleFolder + "/"+files[0]
			dst = BASE_PATH + "Relay_Station" + str(BASE_PORT) + "/rawPebble/" + files[0]
			# dst = "/media/card/Relay_Station10000/" + "rawPebble/" + files[0]

			shutil.move(src,dst)
			pixieMessage = []
			pixieMessage.append("Pixie")
			pixieMessage.append(str("{0:.3f}".format(z_teager_max)))
			tempDateTime = rNTPTime.sendUpdate(server_address, pixieMessage, 5) 



		else: # no new pebble motion data file
			time.sleep(5)

		# iterations += 1
		# if iterations>=4: # heart beat
		# 	iterations = 0
		# 	pixieMessage = []
		# 	pixieMessage.append("Pixie")
		# 	pixieMessage.append(str("{0:.3f}".format(HB_Pixie_Value))) #HB_Pixie_Value = x_max
		# 	tempDateTime = rNTPTime.sendUpdate(server_address, pixieMessage, 5)

			







