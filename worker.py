import os

import redis
from rq import Worker, Queue, Connection
print "in worker"
sys.stdout.flush()
listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
	print "in main"
	sys.stdout.flush()
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()
