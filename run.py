#!flask/bin/python
from app import app
app.run(debug=False, host='0.0.0.0', port=443, ssl_context='adhoc')
