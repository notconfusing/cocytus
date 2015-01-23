import requests
from PUSH_TOKEN_SECRET import PUSH_TOKEN

PUSH_API_URL="http://chronograph.labs.crossref.org/api/push"
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
    rcdicts = [{u'comment': u'', u'wiki': u'enwiki', 'doi': {'deleted': [], 'added': [u'10.1007/s10508-008-9399-9']}, u'server_name': u'en.wikipedia.org', u'title': u'Ephebophilia', u'timestamp': 1421537838, u'server_script_path': u'/w', u'namespace': 0, u'server_url': u'http://en.wikipedia.org', u'id': 707038106, u'length': {u'new': 8401, u'old': 7807}, u'user': u'67.234.187.57', u'type': u'edit', u'bot': False, u'minor': False, u'revision': {u'new': 642974942, u'old': 642974871}},
{u'comment': u'removed no longer needed PBB controls and templates; consistent citation formatting; removed further reading citations that are not specific to this gene', u'wiki': u'enwiki', 'doi': {'deleted': [u'10.1038/ng1285', u'10.1073/pnas.242603899', u'10.1101/gr.2596504'], 'added': []}, u'server_name': u'en.wikipedia.org', u'title': u'RNF40', u'timestamp': 1421537954, u'server_script_path': u'/w', u'namespace': 0, u'server_url': u'http://en.wikipedia.org', u'id': 707038335, u'length': {u'new': 4613, u'old': 5382}, u'user': u'Boghog', u'type': u'edit', u'bot': False, u'minor': False, u'revision': {u'new': 642975132, u'old': 592943590}}, {u'comment': u'- un DOI "\xe0 rallonge" et invalide', u'wiki': u'frwiki', 'doi': {'deleted': [u'10.1002/(SICI)1099-1166(199908)14:8<662::AID-GPS993>3.0.CO;2-4'], 'added': [u'']}, u'server_name': u'fr.wikipedia.org', u'server_script_path': u'/w', u'timestamp': 1421538484, u'title': u"Maladie d'Alzheimer", u'namespace': 0, u'server_url': u'http://fr.wikipedia.org', u'id': 133591348, u'length': {u'new': 157761, u'old': 157823}, u'user': u'BonifaceFR', u'patrolled': True, u'type': u'edit', u'bot': False, u'minor': True, u'revision': {u'new': 111024101, u'old': 110973392}}, {u'comment': u'whoops readd', u'wiki': u'enwiki', 'doi': {'deleted': [], 'added': [u'10.1484/J.Peri.3.434']}, u'server_name': u'en.wikipedia.org', u'title': u'Lagmann mac Gofraid', u'timestamp': 1421538646, u'server_script_path': u'/w', u'namespace': 0, u'server_url': u'http://en.wikipedia.org', u'id': 707039946, u'length': {u'new': 52097, u'old': 51849}, u'user': u'Brianann MacAmhlaidh', u'type': u'edit', u'bot': False, u'minor': False, u'revision': {u'new': 642976429, u'old': 642975807}}]

    for rcdict in rcdicts:
        response = push_to_crossref(rcdict)
        print(response)
