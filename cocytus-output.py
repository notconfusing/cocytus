import sys
import time

import autobahn
from twisted.python import log
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

from rq import Queue
from redis import Redis

import logging
logging.basicConfig(filename='output-results.log', level=logging.INFO)

pwblogger = logging.getLogger("pywiki")
pwbf = logging.Filter("pywiki")
pwbf.filter = lambda record: False
pwblogger.addFilter(pwbf)

redis_con = Redis("tools-redis")

queue = Queue('changes', connection = redis_con)

class WikiCiteServer(ApplicationSession):
	@inlineCallbacks
	def onJoin(self, details):
		logging.info("session ready")

		counter = 0
		while True:
			for change in queue.jobs:
				self.publish(u'com.cocytus.onchange', change)
			yield sleep(1)

if __name__ == "__main__":
	from autobahn.twisted.wamp import ApplicationRunner
	#runner = ApplicationRunner(url = "ws://localhost:12345/citeserver", realm = "realm1")
	#runner.run(WikiCiteServer)
	while True:
		job = queue.dequeue()
		if job is None:
			logging.debug(u'No job found yet, sleeping')
			time.sleep(0.01)
			continue
		if job.result is None:
			logging.debug(u'Job not executed yet; executing: '+str(job))
			job.perform()
		if 'doi' in job.result and isinstance(job.result['doi'], dict) and (job.result['doi']['added'] or job.result['doi']['deleted']): # then one is not empty
			logging.info(u'change detected: '+str(job.result))
		else: # then both are empty
			logging.debug(u'no change detected.')
