import requests
from PUSH_TOKEN_SECRET import PUSH_TOKEN

PUSH_API_URL="http://events.labs.crossref.org/api/push"
PUSH_TYPE="WikipediaCitation"
PUSH_SOURCE="Cocytus"


def push_to_crossref(rcdict):
    for  addremove, doi_list in rcdict['doi'].iteritems():
        for doi in doi_list:
            action = {'added':'add','deleted':'remove'}[addremove]
            article_url = rcdict['server_url'] + '/wiki/' + rcdict['title']
            timestamp = rcdict['timestamp']

            response = requests.post(PUSH_API_URL, json={"doi": doi,
                                              "source": PUSH_SOURCE,
                                              "type": PUSH_TYPE,
                                              "arg1":action,
                                              "arg2":article_url,
                                              "arg3":timestamp}, headers= {"Token": PUSH_TOKEN})
            return response

if __name__ == '__main__':
    #Test
    rcdicts = [{u'comment': u'Reverted 2 edits by [[Special:Contributions/Sciencenerd345|Sciencenerd345]] ([[User talk:Sciencenerd345|talk]]) to last revisioby JorisvS. ([[WP:TW|TW]])', u'wiki': u'enwiki', 'doi': {'deleted': [], 'added': [u'10.1088/0004-637X/736/1/19']}, u'server_name': u'en.wikipedia.org', u'title': u'Kepler-69c', u'timestamp': 1421979373, u'server_script_path': u'/w', u'namespace': 0, u'server_url': u'http://en.wikipedia.org', u'id': 708217572, u'length': {u'new': 13335, u'old': 5262}, u'user': u'Drbogdan', u'type': u'edit', u'bot': False, u'minor': True, u'revision': {u'new': 643758872, u'old': 643755255}}]
    for rcdict in rcdicts:
        response = push_to_crossref(rcdict)
        print(response)
