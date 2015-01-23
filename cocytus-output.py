import sys
import time

import autobahn
from twisted.python import log
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

from rq import Queue
from redis import Redis

from crossref_push import push_to_crossref

import logging
logging.basicConfig(filename='output.log', level=logging.INFO,  format='%(asctime)s %(message)s')
logging.info('process started')
logging.info(str(__name__))
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

#from autobahn.twisted.wamp import ApplicationRunner
#runner = ApplicationRunner(url = "ws://0.0.0.0:12345/citeserver", realm = "realm1")
#runner.run(WikiCiteServer) # this doesn't return

while True:
	job = queue.dequeue()
	if job is None:
		logging.debug(u'No job found yet, sleeping')
		time.sleep(0.1)
		continue
	if job.result is None:
		logging.debug(u'Job not executed yet; executing: '+str(job))
		job.perform()
	
	print(str(job.result))
	if 'doi' in job.result and isinstance(job.result['doi'], dict) and (job.result['doi']['added'] or job.result['doi']['deleted']): # then one is not empty
		logging.info(u'change detected: '+str(job.result))
		#and we have something intriquing to push to crossref
		print("pushing to crossref")
		crossref_response = push_to_crossref(job.results)
		logging.info('pushed to crossref: ' + str(job.result))
		logging.info('crossref response was:' + str(response))
		print("crossref response: " + str(response))
	else: # then both are empty
		logging.debug(u'no change detected.')
