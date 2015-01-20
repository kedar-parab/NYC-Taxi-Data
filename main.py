import os
import webapp2
import jinja2
import time
from datetime import date, time, datetime
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers
from urllib import quote
import sys
import traceback
import json

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
jinja_env.filters['fixurl'] = quote

class WeatherData(db.Model):
	date = db.DateTimeProperty(required = True)
	trips= db.IntegerProperty(required = True)
	temp = db.IntegerProperty(required = True)
	dew_point = db.IntegerProperty(required = True)
	humidity = db.IntegerProperty(required = True)
	sea_level_pressure = db.FloatProperty(required = True)
	visibility_miles = db.IntegerProperty(required = True)
	wind_speed = db.FloatProperty(required = True)
	precipitation = db.StringProperty(required =True)
	cloud_cover = db.IntegerProperty(required = True)
	events = db.StringProperty()

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):   
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        self.render('home.htm')

class WeatherDataHandler(Handler):
	def get(self):
		self.render('upload.htm')

class UploadHandler(Handler, webapp2.RequestHandler):
    def post(self):
        #Our POST Input
        txtinput = self.request.get('txtValue')
        # Create an array
        msg = "Data uploaded"
        array = {'text': msg}

        lines = txtinput.split('\n')
        lines = lines[1:]
        for line in lines:
        	line = line.split('\t')
        	try:
	        	date = datetime.strptime(line[0], "%Y-%m-%d")
	        	trips = int(line[1])
	        	temp = int(line[3])
	        	dew_point = int(line[6])
	        	humidity = int(line[9])
	        	sea_level_pressure = float(line[12])
	        	visibility_miles = int(line[15])
	        	wind_speed = float(line[18])
	        	precipitation = line[20]
	        	cloud_cover = int(line[21])
	        	events = line[22]

	        	a = WeatherData(date = date, trips = trips, temp = temp, dew_point = dew_point, humidity = humidity, sea_level_pressure = sea_level_pressure, visibility_miles = visibility_miles, wind_speed = wind_speed, precipitation = precipitation, cloud_cover = cloud_cover, events = events)
	        	a.put()
	        except Exception, e:
	        	x = e

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(array))

class LineChartHandler(Handler):
	def get(self):
		data = db.GqlQuery("SELECT * FROM WeatherData ORDER BY date")
		self.render('linechart.htm', data = data)

class COHandler(Handler):
	def get(self):
		self.render('co2.htm')

class ParallelChartHandler(Handler):
	def get(self):
		self.render('parallel.htm')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/weather', WeatherDataHandler),
                               ('/upload', UploadHandler),
                               ('/linechart', LineChartHandler),
                               ('/co2', COHandler),
                               ('/parallel', ParallelChartHandler),
                               ],
                              debug=True)
