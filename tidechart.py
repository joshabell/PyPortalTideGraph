import time
import displayio
import json
import adafruit_requests as requests
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.sparkline import Sparkline

TEXT_COLOR          = 0x000CFF
NOW_COLOR           = 0xFFE666
PLOT_COLOR          = 0xFFFFFF
INTERVAL            = 30  # minutes
ENTRIES             = int((24 * 60) / INTERVAL)

class Tidechart:

    def __init__(self, width, height, group, stationid):
        self.width = width
        self.height = height
        self.stationid = stationid
        self.day = -1
       
        cwd = ("/"+__file__).rsplit('/', 1)[0]
        self.text_font = bitmap_font.load_font(cwd+"/fonts/Arial-12.bdf")
        self.text_font.load_glyphs(b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYZ1234567890-')

        self.headline = displayio.Group(max_size = 2, x=0, y = 0)
        self.graph    = displayio.Group(max_size=3, x=0, y=0)

        self.banner   = Label(self.text_font, text="Tide Info / Current Time: 00:00:00", x=7, y=14)
        self.nowline  = Line(0, 30, 0, self.height-30, color=NOW_COLOR)
        self.plot     = Sparkline(int(self.width), int(self.height - 50), x=0, y=25, max_items=ENTRIES, color=PLOT_COLOR)

        self.headline.append(self.banner)
        self.graph.append(self.nowline)
        self.graph.append(self.plot)

        group.append(self.headline)
        group.append(self.graph)

    @property 
    def name(self):
        return 'tidechart'

    def update(self):
        current_time = time.localtime()
        # Once a day, fetch new data
        if (self.day != current_time.tm_mday):            
            data = self._get_data()
            points = self._calc_points(data)
            self.plot.clear_values()
            for p in points:
                self.plot.add_value(int(p))
            self.day = current_time.tm_mday

        self.banner.text = "Tide Info / Current Time: {:02d}:{:02d}:{:02d}".format(current_time.tm_hour, current_time.tm_min, current_time.tm_sec)
        self.nowline.x = self._calc_now_x()
        print(current_time)    
    
    def _get_data(self):
         # Calculate the URL for tide information
        current_time = time.localtime()

        start_time = "{:04d}{:02d}{:02d}".format(current_time.tm_year, current_time.tm_mon, current_time.tm_mday)

        URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&datum=MLLW&time_zone=lst_ldt&units=english&interval=30&format=json&" + \
            "begin_date=" + start_time + "&" + \
            "range=24&" + \
            "station=" + self.stationid

        print("Fetching text from : ", URL)
        r = requests.get(URL)        
        response = r.text
        r.close()
        return response

    def _calc_points(self, json_data):
        data = json.loads(json_data)

        points = []        
        for s in data["predictions"]:       
            tide_height = int((float(s["v"]) * 10))
            points.append(tide_height)
    
        return points

    def  _calc_now_x(self):
        current_time = time.localtime()
        day_percent = ((current_time.tm_hour * 60) + current_time.tm_min) / (24*60)
        x = int(self.width * day_percent)
        return x