# File: /var/www/graas/app.wsgi
import os
# os.chdir(os.path.dirname(__file__))

import bottle
import main

application = bottle.default_app()
