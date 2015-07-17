import requests
import urllib
import logging
from PUSH_TOKEN_SECRET import PUSH_TOKEN
from config import *

def push_to_crossref(rcdict):
    # just printing for debugging purposes
    logging.info(str(rcdict))
    return "yay"
    # real code below
    for  addremove, doi_list in rcdict['doi'].iteritems():
        for doi in doi_list:
            action = {'added':'add','deleted':'remove'}[addremove]
            server_url = rcdict['server_url']
            safe_title = urllib.quote(rcdict['title'].encode('utf-8'))
            article_url = url = "{server_url}/wiki/{safe_title}".format(server_url=server_url, safe_title=safe_title) 
            diff = rcdict['revision']['new']

            response = requests.post(PUSH_API_URL, json={"doi": doi,
                                              "source": PUSH_SOURCE,
                                              "type": PUSH_TYPE,
                                              "arg1":action,
                                              "arg2":article_url,
                                              "arg3":diff}, headers= {"Token": PUSH_TOKEN})
            return response

def heartbeat():
    # printing for debugging purposes
    logging.info("heartbeated")
    return "heart"
    # real code below
    return requests.post(PUSH_API_URL, json={"heartbeat-type": "input", "source": PUSH_SOURCE, "type": PUSH_TYPE},
                                       headers= {"Token": PUSH_TOKEN})

def output_heartbeat():
    # printing for debugging purposes
    logging.info("heartbeated2")
    return "heart2"
    # real code below
    return requests.post(PUSH_API_URL, json={"heartbeat-type": "output", "source": PUSH_SOURCE, "type": PUSH_TYPE},
                                       headers= {"Token": PUSH_TOKEN})

if __name__ == '__main__':
    #Test
    rcdicts = [{u'comment': u'Reverted 2 edits by [[Special:Contributions/Sciencenerd345|Sciencenerd345]] ([[User talk:Sciencenerd345|talk]]) to last revisioby JorisvS. ([[WP:TW|TW]])', u'wiki': u'enwiki', 'doi': {'deleted': [], 'added': [u'10.1088/0004-637X/736/1/19']}, u'server_name': u'en.wikipedia.org', u'title': u'Kepler-69c', u'timestamp': 1421979373, u'server_script_path': u'/w', u'namespace': 0, u'server_url': u'http://en.wikipedia.org', u'id': 708217572, u'length': {u'new': 13335, u'old': 5262}, u'user': u'Drbogdan', u'type': u'edit', u'bot': False, u'minor': True, u'revision': {u'new': 643758872, u'old': 643755255}}]
    for rcdict in rcdicts:
        response = push_to_crossref(rcdict)
        print(response)
