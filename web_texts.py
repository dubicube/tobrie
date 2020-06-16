#########################################################################################
#                                  TEXTS FROM WEB                                       #
#########################################################################################

from urllib import request
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

# Return URL of an image based on msg, using google
def getGoogleImage(msg):
    keys = msg.split(' ')
    keys = [urllib.parse.quote(k) for k in keys]
    data = '+'.join(keys)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    text = requests.get('https://www.google.fr/search?hl=en&tbm=isch&q='+data, headers=headers).text
    l = []
    i = 0
    while i != -1:
        i = text.find("data-id=", i+1)
        k = text.find("\"", i+9)
        l+=[text[i+9:k]]

    # Eventually, more images ID are available in l
    image_id = l[1]
    data = data+"#imgrc="+image_id
    text = requests.get("https://www.google.fr/search?hl=en&tbm=isch&q="+data, headers=headers).text
    pattern = ",\""+image_id+"\",["
    i = text.find(pattern)
    j = text.find("[", i+len(pattern)+1)
    k = text.find("\"", j+2)
    url = text[j+2:k]
    return url

# Download image fropm url
def download_image(url, path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)

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
