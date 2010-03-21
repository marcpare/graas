from bottle import route, run, request, response
import simplejson as json
import memcache
from mako.template import Template

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import StringIO, Image

CACHE_BACKEND = '127.0.0.1:8081'

# @route('/', method='POST')
# def index_post():
#	return "hollo"
#	return generate_charts(request.POST)

@route('/retrieve_plot/:plot_name')
def get_plot(plot_name):
	plot_from_db = mc.get(plot_name)
	
	response.content_type = 'image/png'
	return plot_from_db
		
def request_plot(plot_data):		
	""" returns a dictionary with the results of the plot request """
	
	# test with: http://localhost:8080/generate_plot?data={%22x%22:%20[1,%202,%2010],%20%22y%22:%20[1,%202,%204],%20%22name%22:%20%22asdf2%22,%20%22xlabel%22:%20%22time%22}
	
	if not all([k in plot_data for k in ["x", "y", "name"]]):
		return {"error": "x, y, or name not defined for the requested chart."}
	
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
	
	plot_key = plot_data["name"]
	mc.set(plot_key, imgdata.getvalue())
	
	return {"url" : plot_key}

@route('/generate_plot', method='GET')
def index_get():
	return generate_plot(request.GET)

@route('/generate_plot', method='POST')
def index_post():
	return generate_plot(request.POST)

def generate_plot(request_data):
	# expects the data in the plot format
	# for now this means that x[], y[], and name are defined
	
	if "data" not in request_data:
		plot_result = {"error": "No plot requested."}
	else:	
		try:
			plot_data = json.loads(request_data['data'])
			plot_result = request_plot(plot_data)
		except ValueError:
			plot_result = {"error": "Couldn't decode the JSON input."}
	
	response.content_type = 'text/html'
	return json.dumps(plot_result)

@route('/show', method='GET')
def show_some_plots():
	request_data = request.GET	
	template_string = """
	<html>
	<body>
	<%
	from time import strftime
	%>
	    <p>Generated at ${strftime("%Y-%m-%d %H:%M:%S")}</p>

	    <ul>
	    % for url in charts:
	        <img src="/graas/retrieve_plot/${url}" />
	    % endfor    
	    </ul>

	</body>
	</html>
	
	"""
	
	charts = request_data["names"].split(",")
	mytemplate = Template(template_string)
	return mytemplate.render(charts=charts)

@route('/')
def index():
	return "hello world"

mc = memcache.Client([CACHE_BACKEND], debug=0)
#run(host='localhost', port=8080)	
