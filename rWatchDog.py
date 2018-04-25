from gpio_utils import *
from Constants import *
import rNTPTime
import time
import csv
import struct
import sys
import socket

def watchDog(startDateTime, hostIP, BASE_PORT,  streaming=True, logging=True):