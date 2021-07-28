import time
import board
import displayio
import gc
from tidechart import Tidechart
from adafruit_pyportal import PyPortal

#--| USER CONFIG |--------------------------

# Tide information is obtained from https://tidesandcurrents.noaa.gov
# There you can find your station ID

MY_STATIONID  = "8443970"    # Salem, MA

# Clock drift with the PyPortal is pretty noticable. 
# Number of seconds (roughly) between re-syncs

UPDATE_TIME_INTERVAL = (60 * 60 * 6)  # 6 Hours

#-------------------------------------------

WIDTH = board.DISPLAY.width
HEIGHT = board.DISPLAY.height

pyportal = PyPortal(status_neopixel=board.NEOPIXEL)

# Connect to the internet and get local time
pyportal.get_local_time()

chart = Tidechart(WIDTH, HEIGHT, pyportal.splash, MY_STATIONID)

loop_count = 0
while True:
    chart.update()        
    time.sleep(1)
    loop_count += 1
    if (loop_count == UPDATE_TIME_INTERVAL):
        pyportal.get_local_time()
