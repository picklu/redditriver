import sys
sys.stdout = sys.stderr
sys.path.insert(0, '/var/www/redditriver/app')

# import app from application
from redditriver import app
application = app.wsgifunc()
