from rq import Queue
from redis import Redis

import logging
logging.basicConfig(filename='input.log', level=logging.INFO)

redis_con = Redis(host="tools-redis")

queue = Queue('changes', connection = redis_con)

import compare_change

import socketIO_client

class WikiNamespace(socketIO_client.BaseNamespace):
	def on_change(self, change):
		logging.info(u"enqueing "+str(change))
		queue.enqueue(compare_change.get_changes, change)

	def on_connect(self):
		self.emit(u"subscribe", u"*")

socketIO = socketIO_client.SocketIO(u'stream.wikimedia.org', 80)
socketIO.define(WikiNamespace, u'/rc')

socketIO.wait()
