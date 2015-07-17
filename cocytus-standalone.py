import compare_change
import crossref_push
import socketIO_client
import time
import signal
import logging
from concurrent.futures import ThreadPoolExecutor as PoolExecutor # can do either ProcessPoolEx.. or ThreadPoolEx..
from config import HEARTBEAT_INTERVAL

logging.basicConfig(filename='logs/cocytus.log', level=logging.INFO, format='%(asctime)s %(message)s')
logging.info('cocytus launched')

def handle_result(result):
  logging.info("result is: "+str(result))
  if 'doi' in result and isinstance(result['doi'], dict) and (result['doi']['added'] or result['doi']['deleted']): # one is not empty
    logging.info(u'change detected: '+str(result))
    #and we have something intriguing to push to crossref
    crossref_response = crossref_push.push_to_crossref(result)
    logging.info('pushed to crossref: ' + str(result))
    logging.info('crossref response was:' + str(crossref_response))
  elif type(result) == dict and result["type"] == "heartbeat":
    logging.info("pushing heartbeat")
    crossref_push.push_to_crossref(result)
  else:
    logging.debug(u'no change detected.')

class Queue:
  """not really a work queue just a wrapper for interface compatibility with old redis queue
     submits jobs directly to child workers, no intermediate queue is involved"""
  def __init__(self):
    self.pool = PoolExecutor(max_workers = 64)
    self.live_futures = set()
  def enqueue(self, job, arg = None):
    logging.info("live futures are: "+str(len(self.live_futures)))
    future = self.pool.submit(job, arg)
    self.live_futures.add(future)
    future.add_done_callback(lambda f: (handle_result(f.result(timeout = 30)), self.live_futures.remove(f)))

alarm_interval = HEARTBEAT_INTERVAL # 10 minutes, in prime seconds

queue = Queue()

def alarm_handle(signal_number, current_stack_frame):
	queue.enqueue(crossref_push.heartbeat)
	logging.info('enqueued heartbeat')
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
      except Exception as e:
        logging.error(e.message)
        time.sleep(1.0)

  def on_connect(self):
    self.emit(u"subscribe", u"*")

while True:
  socketIO = socketIO_client.SocketIO(u'stream.wikimedia.org', 80)
  socketIO.define(WikiNamespace, u'/rc')
  socketIO.wait(HEARTBEAT_INTERVAL + 2) # 10 minutes, in prime seconds

