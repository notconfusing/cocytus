This is the Cocytus project for tracking citations on Wikipedia.

How it Works
------------
We are changing a __diff stream__ into a __citation delta__ stream.

+ we use the [recent changes stream](https://wikitech.wikimedia.org/wiki/RCStream)
+ to make queue of diffs to be inspected
+ Keep a database table of the latest version we have seen so far
+ call the wikimedia api to fetch th diff text
+ see if the diff involves adding or removing a DOI or other citation identifier
+ publish a stream (websocket or pubsubhubbub) of:
    + Idenfifier, delta direction, provenance page, page metadata

How to run it
-------------

You'll need to have Redis Queue (rq) and autobahn[twisted] and crossbar installed.
You'll also want to have wikimedia labs compatible (Sun Grid Engine compatible) job scripting
since our highest level scripts use grid engine to manage the jobs.

+ start up the redis server (If you're running on wikimedia labs this is already running on tools-redis.)
+ start up crossbar using the config in the 'changes' directory
+ run submit-cocytus.sh to get the queue workers working and start pushing the input to the POST endpoint

If you want to manually manage the jobs the flow goes like this:

+ start cocytus-input.py and background the job (this listens on RCstream and fills the queue with jobs that fetch diff info)
+ start an rqworker on the 'changes' queue and background the job
+ start cocytus-output.py and background the job (this serves the fetched diff info)
+ start cocytus-client.py (this connects to the cocytus-output server and shows what it is serving)

