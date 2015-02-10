from rq import Queue
from redis import Redis
import compare_change
import socketIO_client
import time
import signal
import logging
from config import REDIS_LOCATION, HEARTBEAT_INTERVAL

logging.basicConfig(filename='logs/input.log', level=logging.INFO, format='%(asctime)s %(message)s')
logging.info('program launched')


redis_con = Redis(host=REDIS_LOCATION)

queue = Queue('changes', connection = redis_con)
logging.info('redis connected')

alarm_interval = HEARTBEAT_INTERVAL # 10 minutes, in prime seconds

def alarm_handle(signal_number, current_stack_frame):
	queue.enqueue(heartbeat)
	
	signal.alarm(alarm_interval)

signal.signal(signal.SIGALRM, alarm_handle)
signal.siginterrupt(signal.SIGALRM, False)
signal.alarm(alarm_interval)

class WikiNamespace(socketIO_client.BaseNamespace):

	def on_change(self, change):
		logging.info(u"enqueing "+str(change))
		while True:
			try:
                        	queue.enqueue(compare_change.get_changes, change)
				break
			except redis.exceptions:
				time.sleep(1.0)

	def on_connect(self):
		self.emit(u"subscribe", u"*")


while True:
	socketIO = socketIO_client.SocketIO(u'stream.wikimedia.org', 80)
	socketIO.define(WikiNamespace, u'/rc')
	socketIO.wait(HEARTBEAT_INTERVAL + 2) # 10 minutes, in prime seconds
