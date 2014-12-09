This is the Cocytus project for tracking citations on Wikipedia.

How it Works
------------
We are chaning a __diff stream__ into a __citation delta__ stream.  

+ we use the [recent changes stream](https://wikitech.wikimedia.org/wiki/RCStream) 
+ to make queue of diffs to be inspected
+ Keep a database table of the latest version we have seen so far
+ call the wikimedia api to fetch th diff text
+ see if the diff involves adding or removing a DOI or other citation identifier
+ publish a stream (websocket or pubsubhubbub) of:
    + Idenfifier, delta direction, provenance page, page metadata