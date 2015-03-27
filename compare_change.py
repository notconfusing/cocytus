#you need max's patched pywikibot to get site.compare.
import pywikibot
from bs4 import BeautifulSoup
import mwparserfromhell
import json
import ast
import time
import logging
import mwcites.extractors.doi

def wikitext_of_interest(wikitext):
    return set(ident.id for ident in mwcites.extractors.doi.extract(wikitext))
    
def single_comparator(page):
    comparands = {'deleted': [] , 'added': []}
    
    try:
        wikitext = page.get()
    except pywikibot.exceptions.IsRedirectPage:
        redir_target =  page.getRedirectTarget()
        #only trying one layer of redirect
        try:
            wikitext = redir_target.get()
            comparands['redirect'] = redir_target.title()
        except:
            return None
            #log this
    except pywikibot.exceptions.NoPage:
        return None
        #log this

    interests = wikitext_of_interest(wikitext)
    comparands['added'] = list(interests)
    return comparands

def comparator(compare_string):
    comparands = {'deleted':set() , 'added': set()}
    soup = BeautifulSoup(compare_string)
    for change_type, css_class in (('deleted', 'diff-deletedline'),('added', 'diff-addedline')):
        changes = set()
        crutons = soup.find_all('td', class_=css_class)
        for cruton in crutons:
            cruton_string = ''.join(list(cruton.strings))
            interests = wikitext_of_interest(cruton_string)
            changes.update(interests)
        comparands[change_type].update(changes)

    uniq_comparands = dict()
    uniq_comparands['added'] = list(comparands['added'].difference(comparands['deleted']))
    uniq_comparands['deleted'] = list(comparands['deleted'].difference(comparands['added']))
    
    return uniq_comparands
    

def make_family(server_name):
    parts = map(lambda x: x.lower(), server_name.split('.'))
    if parts[0] == 'commons':
        return ('commons','commons')
    if parts[1] == 'wikidata':
        return ('wikidata', 'wikidata')
    if parts[0] == 'meta':
        return ('meta', 'meta')
    if parts[0] == 'incubator':
        return ('incubator', 'incubator')
    if parts[0] == 'species':
        return ('species', 'species')
    else:
        return parts[0], parts[1]

def get_changes(rcdict):
    '''Get the changes of dois that occured in an rcdict
    @returns dict of lists of 'added' or 'deleted' dois
    or None if there was an error (like deleted history).
    Also handles newly created pages.
    '''
    try:
        server_name = rcdict['server_name']
        lang, fam = make_family(server_name)
        if 'timestamp' in rcdict:
            rcdict['time'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(rcdict['timestamp']))
        #if it's an edit

        if rcdict['type'] == 'edit':
            from_rev, to_rev = rcdict['revision']['old'], rcdict['revision']['new']
            api_to_hit = pywikibot.Site(lang, fam)
            comparison_response = api_to_hit.compare(from_rev, to_rev)
            comparison_string = comparison_response['compare']['*']
            rcdict['doi'] = comparator(comparison_string)
        #if its a new page
        if rcdict['type'] == 'new':
            title = rcdict['title']
            api_to_hit = pywikibot.Site(lang, fam)
            page = pywikibot.Page(api_to_hit, title)
            rcdict['doi'] = single_comparator(page)
        #log this or do something else
        if rcdict['type'] == 'log':
            logging.debug("logging_event" + str(rcdict))
        else:
            logging.debug('Not an edit, new page, or logging event '+str(rcdict))
        return rcdict

    except pywikibot.data.api.APIError as e:
        logging.debug(e.message + str(rcdict))
        return rcdict
    except Exception as e:
        logging.debug(e.message + str(rcdict))
        return rcdict

    
    
if __name__ == '__main__':
    #test

    print get_changes({u'comment': u'sp, replaced: Bogomolov Jr. \u2192 Bogomolov jr. (5), Santiago Ventura Bertomeu \u2192 Santiago Ventura met [[Project:AWB|AWB]]', u'wiki': u'nlwiki', u'type': u'edit', u'server_name': u'nl.wikipedia.org', u'server_script_path': u'/w', u'timestamp': 1420063846, u'title': u'ATP-toernooi van Newport 2009', u'namespace': 0, u'server_url': u'http://nl.wikipedia.org', u'length': {u'new': 10649, u'old': 10658}, u'user': u'Den Hieperboree', u'patrolled': False, u'bot': False, u'id': 66286621, u'minor': False, u'revision': {u'new': 42892757, u'old': 36109902}})
    print get_changes({'revision':{'old':638680435,'new':638682695}, 'server_name':'en.wikipedia.org', 'type':'edit'})
    print get_changes({'revision':{'old':638680344,'new':638680435}, 'server_name':'en.wikipedia.org', 'type':'edit'})
    print get_changes({'revision':{'old':None,'new':638680344}, 'server_name':'en.wikipedia.org', 'type':'new', 'title':'User:Maximilianklein/cocytusbox'})
    print get_changes({'revision':{'old':639823863,'new':640446344}, 'server_name':'en.wikipedia.org', 'type':'edit'})

    '''
    testfile = open('dumps.txt','r')
    lines = testfile.readlines()
    
    output = []
    for line in lines:
        rcdict = ast.literal_eval(line)
        result = get_changes(rcdict)
            #log
        if result:
            output.append(result)
            json.dump(output, open('munged.json','w'))
    '''
