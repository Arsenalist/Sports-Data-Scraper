import sys
from flask import Flask, send_file, make_response, request
from sportsparser import Controller

from rq import Queue
import time

import redis
import os

app = Flask(__name__) 
app.config.from_pyfile('config.py')

@app.route('/playbyplay', methods=['GET'])
def playbyplay_form():
	return "<form action='/playbyplay' method='post'><input type='text' name='date' placeholder='mmddyyyy'><input type='text' name='email' placeholder='Enter email here'/><input type='submit' value='Submit'/></form>"


@app.route('/playbyplay', methods=['POST'])
def generate_csv():
	print "hi there"
	date = request.form["date"]
	email = request.form["email"]
	print date
	print email
	sys.stdout.flush()

	redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
	conn = redis.from_url(redis_url)
	q = Queue(connection=conn)
	date_obj = time.strptime(date, "%m%d%Y")   
	date_normalized = time.strftime("%Y%m%d", date_obj)
	headers = { 'Content-Type': 'application/zip', 
	            'Content-Disposition': 'attachment; filename=playbyplay_' + date +'.zip'}
	c = Controller()
	result = q.enqueue(c.playbyplay_handler, date_normalized, email)
	return "A file will be emailed to you very shortly."

	#zip_bytes = c.convert_to_bytes(files[0], files[1])
	#return make_response(zip_bytes, 200, headers)


if __name__ == '__main__':
	print "hello"
	app.run(debug=True)

