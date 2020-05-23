########################################################################################################################################################
#                                                                TEXTS FROM WEB                                                                        #
########################################################################################################################################################



import requests
import urllib.parse
import html
import re

# Infinite regex poweeeerrrrr
# Requests google with "msg" as researched text
# Return the first important result found
def getGoogleResponse(msg):
    keys = msg.split(' ')
    keys = [urllib.parse.quote(k) for k in keys]
    data = '+'.join(keys)
    text = html.unescape(requests.get('https://www.google.com/search?q='+data).text)
    regex_r = re.search('(?<=<div class="BNeawe iBp4i AP7Wnd">)(?:(?!<div>).)*?(?=</div>)', text)
    if regex_r != None:
        txt_rep = regex_r.group(0)
        return txt_rep
    regex_r = re.search('(?<=<div class="BNeawe s3v9rd AP7Wnd">)(?!<div>)(?:(?!<div>).)*?(?=</div>)', text)
    if regex_r != None:
        txt_rep = regex_r.group(0)
        while "<" in txt_rep:
            a = txt_rep.index("<")
            b = txt_rep.index(">")
            txt_rep = txt_rep[0:a]+txt_rep[b+1:]
        return txt_rep
    return ""

# Get a random phrase with no sense
def getQuote():
    text = requests.get('http://generateur.vuzi.fr/').text
    i = text.index('<span id="quotemarkContent">')
    j = text.index('</span>', i)
    return text[i+37:j-6]

# Get a random information
def getInfo():
    text = requests.get('https://www.savoir-inutile.com/').text
    i = text.index('<h2 id="phrase"')
    j = text.index('</h2>', i)
    return text[i+39:j]
