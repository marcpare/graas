# File: /var/www/graas/app.wsgi
import os
import monitor
import bottle
import main

os.chdir(os.path.dirname(__file__))

monitor.start(interval=1.0)
# In case we want to track any non-Python files
# monitor.track(os.path.join(os.path.dirname(__file__), 'site.cf'))

application = bottle.default_app()
