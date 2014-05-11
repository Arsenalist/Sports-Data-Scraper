import sys
from flask import Flask, send_file, make_response
from sportsparser import Controller
from worker import conn
from rq import Queue
import time

app = Flask(__name__) 
app.config.from_pyfile('config.py')

@app.route('/playbyplay/<date>/<email>')
def generate_csv(date, email):
	q = Queue(connection=conn)
	date_obj = time.strptime(date, "%m%d%Y")   
	date_normalized = time.strftime("%Y%m%d", date_obj)
	headers = { 'Content-Type': 'application/zip', 
	            'Content-Disposition': 'attachment; filename=playbyplay_' + date +'.zip'}
	c = Controller()
	print "about to do the worker"
	sys.stdout.flush()
	result = q.enqueue(c.playbyplay_handler, date_normalized, email)
	print "did the worker"
	sys.stdout.flush()
	return "A file will be emailed to you very shortly."

	#zip_bytes = c.convert_to_bytes(files[0], files[1])
	#return make_response(zip_bytes, 200, headers)


if __name__ == '__main__':
	print "hello"
	app.run(debug=True)

