from rq import Queue
from redis import Redis
import compare_change
import socketIO_client

import logging

logging.basicConfig(filename='input.log', level=logging.INFO, format='%(asctime)s %(message)s')

logging.info('program launched')
redis_con = Redis(host="tools-redis")

queue = Queue('changes', connection = redis_con)
logging.info('redis connected')

class WikiNamespace(socketIO_client.BaseNamespace):
	def on_change(self, change):
		logging.info(u"enqueing "+str(change))
		queue.enqueue(compare_change.get_changes, change)

	def on_connect(self):
		self.emit(u"subscribe", u"*")

socketIO = socketIO_client.SocketIO(u'stream.wikimedia.org', 80)
socketIO.define(WikiNamespace, u'/rc')


socketIO.wait()
