This is the Cocytus project for tracking citations on Wikipedia.

# How it Works

We are changing a __diff stream__ into a __citation delta__ stream.

+ we use the [recent changes stream](https://wikitech.wikimedia.org/wiki/RCStream)
+ to make queue of diffs to be inspected
+ Keep a database table of the latest version we have seen so far
+ call the wikimedia api to fetch the diff text
+ call the Wikimedia API to fetch the diff text
+ see if the diff involves adding or removing a DOI or other citation identifier
  + we do this in three different ways:
	1. run a regex on the diff text
	1. look for `doi=xxx` patterns in templates
	1. look for `[[doi:xxx]]` external links.
+ then for each change found we push that change to crossref in `crossref_push.py` with information
    + Idenfifier, delta direction, provenance page, page metadata
    + which can be viewed at [crossreflabs](http://events.labs.crossref.org/events/types/WikipediaCitation)

# How to run it

## Configuration

+ virtualenv
  we use a virtualenv for this project. If it's ever assumed the env should be located at ~/c-env

+ pywikibot
  + pywikibot needs a user-config.py file to run. However since we are only ever reading from the mediawiki API and never writing, having this user-config.py file is only a formality to shut-up pywikibot. For this you can copy user-config.py.sample file and just enter in a valid username.

You'll need to have Redis Queue (rq) and autobahn[twisted] and crossbar installed.
You'll also want to have wikimedia labs compatible (Sun Grid Engine compatible) job scripting
since our highest level scripts use grid engine to manage the jobs.

+ config files
  + There are two config files, one is not in the repository because it contains secret information, so you must add it.
  + PUSH_TOKEN is the secret config file containing the token used to POST results to crossref. It should contain an assignment to the variable `PUSH_TOKEN_SECRET`
  + config.py contains all other configuration information and has sensible defaults for running on wikimedia labs

## Launching

+ First steps
  + start up the redis server (If you're running on wikimedia labs this is already running on tools-redis.) If you're running your own, edit submit-cocytus.sh to point to it.

+ If you are using Sun Grid Engine or the like which is available on wikimedia labs:
  + `bash submit-cocytus.sh` will start sixteen workers on each of the main work queue and the failure queue; this is a sensible number to keep up with changes
  + `bash killgrid.sh` will delete all the current users jobs which will stop the queue workers

+ If you want to manually manage the jobs instead of using the Grid Engine the flow goes like this (see `submit-cocytus.sh` for relevant job parameters:
  + start cocytus-input.py and background the job (this listens on RCstream and fills the queue with jobs that fetch diff info)
  + start an rqworker on the 'changes' queue and background the job (this asynchronously fetches and processes changes associated with edits and puts the results back in the queue)
  + start cocytus-output.py and background the job (this POSTs the processed info to the endpoint)

# Running

Logs will go into the `logs` subdirectory of where the processes are launched.

# Future work
+ Get changes directly from the redis changes queue instead of the RC stream
+ publish a websocket or pubsubhubub stream in addition to or instead of pushing changes with HTTP POSTs
+ listening for and publishing arbitrary changes
+ summary information about changes
+ natural language modelling of changing wikipedia discourse informed by changes stream
