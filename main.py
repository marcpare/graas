from config import *

from bottle import route, run, request, response
import simplejson as json
import memcache
from bottle import mako_view as view

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import StringIO, Image

@route('/plot', method="GET")
def get_plot():
	return do_plot(request.GET)
	
@route('/plot', method="POST")	
def post_plot():
	return do_plot(request.POST)
		
def do_plot(request_data):
	result = generate_plot(request_data)
	if result["status"] == "success":
		return serve_image(result["image_data"])
	else:
		return result["message"]

def serve_image(image_data):
	response.content_type = 'image/png'
	return image_data
	
def generate_plot(request_data):
	# expects the data in the plot format
	# for now this means that x[], y[], and name are defined
	if "data" not in request_data:
		plot_result = {"status": "error", "message": "No plot requested."}
	else:	
		try:
			plot_data = json.loads(request_data['data'])
			plot_result = request_plot(plot_data)
		except ValueError:
			plot_result = {"status": "error", "message": "Couldn't decode the JSON input."}

	response.content_type = 'text/html'
	return plot_result
		
def request_plot(plot_data):		
	""" returns a dictionary with the results of the plot request """
	
	# test with: http://localhost:8080/generate_plot?data={%22x%22:%20[1,%202,%2010],%20%22y%22:%20[1,%202,%204],%20%22name%22:%20%22asdf2%22,%20%22xlabel%22:%20%22time%22}
	
	if not all([k in plot_data for k in ["x", "y", "name"]]):
		return {"result": "error", "message": "x, y, or name not defined for the requested chart."}
	
	# Do the plot
	fig = plt.figure()
	fig.set_size_inches((5,4))
	
	plt.plot(plot_data["x"], plot_data["y"], "bo")
	plt.title(plot_data["name"])
	
	if "xlabel" in plot_data:
		plt.xlabel(plot_data["xlabel"])
	if "ylabel" in plot_data:
		plt.ylabel(plot_data["ylabel"])
	
	# store the generated charts in memcached
	imgdata = StringIO.StringIO()
	fig.savefig(imgdata, format='png')
	
	return {"status" : "success", "image_data" : imgdata.getvalue()}

@route('/')
@view('index')
def index():
	return {}

# mc = memcache.Client([CACHE_BACKEND], debug=0)

if ENVIRONMENT == "development":
	run(reloader=True, host=HOST, port=PORT)	

