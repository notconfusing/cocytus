#you need max's patched pywikibot to get site.compare.
import pywikibot
from bs4 import BeautifulSoup
import mwparserfromhell
import re
import json
import ast

#print(pywikibot.__file__)

def wikitext_of_interest(wikitext):
    interests = set()
    wikicode = mwparserfromhell.parse(wikitext)
    #is it in a template of doi=xxxx style?
    for template in wikicode.filter_templates():
        for param in template.params:
            if param.name.encode('utf-8').strip().lower() == 'doi':
                interests.add(param.value.strip())
    #is it in a  wikilink of [[doi:xxxx]] style?
    for link in wikicode.filter_wikilinks():
        link_parts = link.title.split(':')
        if link_parts[0].lower() == 'doi':
            interests.add(link_parts[1].split())
    return interests
    
    
def single_comparator(page):
    comparands = {'deleted': [] , 'added': []}
    
    try:
        wikitext = page.get()
    except pywikibot.exceptions.IsRedirectPage:
        redir_target =  page.getRedirectTarget()
        #only trying one layer of redirect
        try:
            wikitext = redir_target.get()
        except:
            pass
    except pywikibot.exceptions.NoPage:
        pass

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
    parts = server_name.split('.')
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
    server_name = rcdict['server_name']
    lang, fam = make_family(server_name)
    #if it's an edit
    if rcdict['type'] == 'edit':
        from_rev, to_rev = rcdict['revision']['old'], rcdict['revision']['new']
        api_to_hit = pywikibot.Site(lang, fam)
        comparison_response = api_to_hit.compare(from_rev, to_rev)
        comparison_string = comparison_response['compare']['*']
        return comparator(comparison_string)
    #if its a new page
    if rcdict['type'] == 'new':
        title = rcdict['title']
        api_to_hit = pywikibot.Site(lang, fam)
        page = pywikibot.Page(api_to_hit, title) 
        return single_comparator(page)
    #log this or do something else
    if rcdict['type'] == 'log':
        pass #log

    
    
if __name__ == '__main__':
    #test
    '''
    print compare({'revision':{'old':638680435,'new':638682695}, 'server_name':'en.wikipedia.org'})
    print compare({'revision':{'old':638680344,'new':638680435}, 'server_name':'en.wikipedia.org'})
    print compare({'revision':{'old':None,'new':638680344}, 'server_name':'en.wikipedia.org'})
    '''
    
    testfile = open('dumps.txt','r')
    lines = testfile.readlines()
    
    output = []
    for line in lines:
        rcdict = ast.literal_eval(line)
        try:
            result = get_changes(rcdict)
        except Exception as e:
            print e
            print rcdict
        if result:
            output.append(result)
            json.dump(output, open('munged.json','w'))
    