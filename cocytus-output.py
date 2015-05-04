import sys
import time
import string

import autobahn
from twisted.python import log
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

from rq import Queue
from redis import Redis
from config import REDIS_LOCATION, HEARTBEAT_INTERVAL

from crossref_push import push_to_crossref

import logging
logging.basicConfig(filename='output.log', level=logging.INFO,  format='%(asctime)s %(message)s')
logging.info('process started')
pwblogger = logging.getLogger("pywiki")
pwbf = logging.Filter("pywiki")
pwbf.filter = lambda record: False
pwblogger.addFilter(pwbf)

alarm_interval = HEARTBEAT_INTERVAL # 10 minutes, in prime seconds

import signal
def alarm_handle(signal_number, current_stack_frame):
	crossref_push.output_heartbeat
	logging.info('pushed output heartbeat')
	signal.alarm(alarm_interval)

signal.signal(signal.SIGALRM, alarm_handle)
signal.siginterrupt(signal.SIGALRM, False)
signal.alarm(alarm_interval)

redis_con = Redis(REDIS_LOCATION)

queue = Queue('changes', connection = redis_con, default_timeout = 10) #seconds

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
		print('no job ffound yet, sleeping')
		logging.debug(u'No job found yet, sleeping')
		time.sleep(1)
		continue
	if job.result is None:
		print('job unexecuted: '+ str(job))
		logging.debug(u'Job not executed yet; executing: '+str(job))
		job.perform()
	
	print("Job result is "+str(job.result))
	if 'doi' in job.result and isinstance(job.result['doi'], dict) and (job.result['doi']['added'] or job.result['doi']['deleted']): # one is not empty
		logging.info(u'change detected: '+str(job.result))
		#and we have something intriquing to push to crossref
		print("pushing to crossref")
		crossref_response = push_to_crossref(job.result)
		logging.info('pushed to crossref: ' + str(job.result))
		logging.info('crossref response was:' + str(crossref_response))
		print("crossref response: " + str(crossref_response))
	elif type(job.result) == dict and job.result["type"] == "heartbeat":
		logging.info("pushing heartbeat")
		push_to_crossref(job.result)
	else:
		logging.debug(u'no change detected.')
