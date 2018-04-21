#!flask/bin/python
from app import app
from werkzeug.contrib.fixers import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)
app.run(host='0.0.0.0',ssl_context=('fullchain.pem', 'privkey.pem'))
