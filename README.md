This is the Cocytus project for tracking citations on Wikipedia.

How it Works
------------
We are changing a __diff stream__ into a __citation delta__ stream.

+ we use the [recent changes stream](https://wikitech.wikimedia.org/wiki/RCStream)
+ to make queue of diffs to be inspected
+ Keep a database table of the latest version we have seen so far
+ call the wikimedia api to fetch the diff text
+ see if the diff involves adding or removing a DOI or other citation identifier
  + we do this in three different ways:
	1. run a regex on the diff text
	1. look for `doi=xxx` patterns in templates
	1. look for `[[doi:xxx]]` external links.
+ then for each change found we push that change to crossref in `crossref_push.py`
    + which can be viewed at [crossreflabs](http://events.labs.crossref.org/events/types/WikipediaCitation)

How to run it
-------------

Configuration
-------------
-------------
+ virtualenv
  we use a virtualenv for this project. If it's ever assumed the env should be located at ~/c-env

+ pywikibot
  + pywikibot needs a user-config.py file to run. However since we are only ever reading from the mediawiki API and never writing, having this user-config.py file is only a formality to shut-up pywikibot. For this you can copy user-config.py.sample file and just enter in a valid username.

You'll need to have Redis Queue (rq) and autobahn[twisted] and crossbar installed.
You'll also want to have wikimedia labs compatible (Sun Grid Engine compatible) job scripting
since our highest level scripts use grid engine to manage the jobs.

Launching
---------
---------

+ start up the redis server (If you're running on wikimedia labs this is already running on tools-redis.)
+ start up crossbar using the config in the 'changes' directory
+ run submit-cocytus.sh to get the queue workers working and start pushing the input to the POST endpoint

If you want to manually manage the jobs the flow goes like this:

+ start cocytus-input.py and background the job (this listens on RCstream and fills the queue with jobs that fetch diff info)
+ start an rqworker on the 'changes' queue and background the job
+ start cocytus-output.py and background the job (this serves the fetched diff info)
+ start cocytus-client.py (this connects to the cocytus-output server and shows what it is serving)

