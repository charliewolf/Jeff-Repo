#!/usr/bin/python

from gpiozero import MotionSensor
from datetime import datetime
from time import time, sleep
from picamera import PiCamera, Color
import sqlite3
from slackclient import SlackClient
import os

token = os.environ["JAZZBOT_KEY"]
conn = sqlite3.connect('monitoring.db')
c = conn.cursor()

sc = SlackClient(token)

camera = PiCamera()
camera.framerate = 60
pir = MotionSensor(4)
camera.resolution = (1280,960)
camera.annotate_background = Color('black')
camera.hflip = True


if sc.rtm_connect():
  posttime = 0
  while True:
    pir.wait_for_motion()
    sleep(0.5)
    filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    camera.annotate_text = filename
    camera.capture('/home/pi/Desktop/Motion_Pics/%s.jpg' % filename)
#    camera.start_recording('/home/pi/Desktop/Motion_Vids/%s.h264' % filename)
    try:
      c.execute("INSERT INTO motion VALUES ('bedroom',date(),time())")
      conn.commit()
    except Exception as e:
      print e
    if posttime == 0 or posttime - datetime.datetime.now().time() > 8:
      try:      
        sc.api_call(
         'files.upload',
         channels="#jazzbot_test",
         filename='Motion Detected',
         file=open('/home/pi/Desktop/Motion_Pics/%s.jpg' % filename, 'rb')
         )
        posttime = datetime.datetime.now().time()
      except Exception as e:
        print e

#    pir.wait_for_no_motion()
#    camera.stop_recording()

else:
  print "bad connection"
