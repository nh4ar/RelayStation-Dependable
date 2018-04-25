from libpebble2.communication import PebbleConnection
import logging
from libpebble2.communication.transports.serial import SerialTransport as ST
import libpebble2.exceptions
from libpebble2.protocol import *
from libpebble2.services.appmessage import AppMessageService, CString, Uint8
from libpebble2.services.data_logging import DataLoggingService
from time import sleep
import subprocess
import sys
import redis
import os
from serial.serialutil import SerialException
import argparse

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("pebble_id", type=int)
parser.add_argument("streaming_port", type=str)
args = parser.parse_args()

#magic number for pebble app
SESSION_TAG = 0x54
running = True

#redis_ip = os.environ["REDIS_IP"]
#relay_id = os.environ["RELAY_ID"]

#r = redis.StrictRedis(host=redis_ip, port=6379, db=0)

def get_id(sessions):
        for session in sessions:
                if session['log_tag'] == SESSION_TAG:
                        infomsg = "FOUND ID " + str(session['session_id'])
                        logging.info(infomsg)
                        return session['session_id']
        return -1

logging.info("Starting pebble connection")


pebble = PebbleConnection(ST("/dev/rfcomm0"), log_packet_level=logging.DEBUG)
pebble.connect()
pebble.pump_reader()
try:
    while running:
            try:
                logging.info("Attempting to connect to pebble")
                pebble.run_async()
                logging.info("Pebble connection success")
                break
            except libpebble2.exceptions.TimeoutError:
                logging.info("Pebble timeouted, retrying..")
            continue

    while pebble.connected:

        data_srv = DataLoggingService(pebble,5000)
        data_srv.set_send_enable(True)

        logging.info("Looking for target session")
        # Update target session id
        target_session_id = get_id(data_srv.list())

        # if we could not find it retry
        while target_session_id == -1:
            logging.info("target session not found")
            sleep(3)
            target_session_id = get_id(data_srv.list())

        # start the data stream. If this returns then the stream has stopped
        (session_info, data) = data_srv.download(target_session_id)
        logging.info("stream closed")

        sleep(1)

except SerialException:
    print("Pebble disconnected unexpectedly")
    #pebble.close()
    exit(2)
