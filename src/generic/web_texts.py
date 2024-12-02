#########################################################################################
#                                  TEXTS FROM WEB                                       #
#########################################################################################

from urllib import request
import requests
import urllib.parse
import html
import re



def getLocalData(data, i0):
    p = 1
    while(data[i0] != '<'):
        i0+=1
    i = i0+1
    while p > 0:
        if data[i:i+4] == "<div" or data[i:i+5] == "<span":
            p+=1
        elif data[i:i+5] == "</div" or data[i:i+6] == "</span":
            p-=1
        i+=1
    i1 = data.find('>', i)
    return data[i0:i1]
def removeStructure(data):
    r = ""
    keep = True
    string = False
    for d in data:
        if (not keep) and d == '"':
            string = True
        if string and d == '"':
            string = False
        if not string:
            if keep and d == '<':
                keep = False
            if (not keep) and d == '>':
                keep = True
        if keep:
            if d != '>':
                r+=d
            #elif len(r) == 0 or r[-1] != '\n':
            #    r+='\n'
    return ' '.join([e for e in r.split(' ') if e != ''])

# Requests google with "msg" as researched text
# Return the first important result found
def getGoogleResponse(msg):
    keys = msg.split(' ')
    keys = [urllib.parse.quote(k) for k in keys]
    data = '+'.join(keys)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    text = html.unescape(requests.get('https://www.google.com/search?q='+data, headers=headers).text)


    results = []

    # Big responses on top
    i = 0
    while i != -1:
        i = text.find('aria-level="3" role="heading"', i)
        if i != -1:
            while(text[i] != '<'):
                i-=1
            if text[i:i+31] == '<div class="HwtpBd gsrt PZPZlf"':
                s = removeStructure(getLocalData(text, i))
                print(7, s)
                results += [["Top", s]]
            while(text[i] != '>'):
                i+=1

    # Detect interesting blocs
    il = [text.find('<h2 class="Uo8X3b"')]
    while il[-1] != -1:
        il += [text.find("<h2", il[-1]+1)]
    responses = []
    for i in il:
        if i != -1:
            j = text.find('</h2>', i)
            if j != -1:
                responses += [text[i:j+5]+"\n"+getLocalData(text, j+5)]

    calc_result = ""
    for r in responses:
        # Title of bloc
        a = r.find('>')
        b = r.find('</h2>')
        title = r[a+1:b]
        #print("\n"+title)
        # Huge text
        i = r.find('aria-level="3"')
        if i != -1:
            i = r.find('>', i)
            j = r.find('<', i)
            #print(4, r[i+1:j])
            results += [[title, r[i+1:j]]]
        # Text between span
        i = 0
        while i != -1:
            i = r.find('<span', i)
            if i != -1:
                i = r.find('>', i)
                j = r.find('</span', i)
                s = r[i+1:j].strip()
                #print(6, s)
                results += [[title, s]]
                if title == "Résultat de calculatrice":
                    calc_result = s

    #print(results)
    local_time = []
    for r in results:
        if r[0] == "Heure locale":
            local_time+=[r[1]]
    local_time = "\n".join(local_time)

    if len(local_time) > 0:
        return local_time
    if len(calc_result) > 0:
        return calc_result

    for r in results:
        if r[0] == "Description":
            return r[1]

    for r in results:
        if r[0] == "Extrait optimisé sur le Web":
            return r[1]

    if len(results) > 0:
        return results[0][1]

    # Description
    # Extrait optimisé sur le Web
    # Résultat de calculatrice
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
    li = 0
    loop = True
    url = ""
    while li<len(l) and loop:
        li+=1
        image_id = l[li]
        data2 = data+"#imgrc="+image_id
        text = requests.get("https://www.google.fr/search?hl=en&tbm=isch&q="+data2, headers=headers).text
        pattern = ",\""+image_id+"\",["
        i = text.find(pattern)
        j = text.find("[", i+len(pattern)+1)
        k = text.find("\"", j+2)
        url = text[j+2:k]
        if url.split(".")[-1] in ["png", "jpg", "gif"]:
            loop = False
    if li==len(l):return ""

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
    text = requests.get('http://generateur.vuzi.fr/', verify=False).text
    i = text.index('<span id="quotemarkContent">')
    j = text.index('</span>', i)
    return text[i+37:j-6]

# Get a random information
def getInfo():
    text = requests.get('https://www.savoir-inutile.com/').text
    i = text.index('<h2 id="phrase"')
    j = text.index('</h2>', i)
    return text[i+39:j]


# Aliexpress

def parseAlieContent(p, key):
    i = p.find('"'+key+'":"', 0)+4+len(key)
    j = p.find('"', i)
    return p[i:j]
def parseAlieProduct(p):
    title = parseAlieContent(p, 'title')
    imageUrl = 'https:' + parseAlieContent(p, 'imageUrl')
    return [title, imageUrl]
def parseAlie(msg):
    keys = msg.split(' ')
    keys = [urllib.parse.quote(k) for k in keys]
    data = '+'.join(keys)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    text = requests.get('https://fr.aliexpress.com/wholesale?catId=0&initiative_id=SB_20200827111753&SearchText='+data, headers=headers).text
    i = text.find('"items"', 0)+9
    j = i
    p = 1
    while p != 0:
        if text[j] == '[':
            p+=1
        if text[j] == ']':
            p-=1
        j+=1
    data = text[i+1:j-2].split('},{')
    return data
def getFirstAlie(msg):
    d = parseAlie(msg)
    return parseAlieProduct(d[0])





def getRandomWiki():
    text = requests.get('https://en.wikipedia.org/wiki/Special:Random', verify=False).text
    gzjhsgkjhqes = '<link rel="canonical" href="'
    i = text.index(gzjhsgkjhqes)
    j = text.index('">', i)
    return text[i+len(gzjhsgkjhqes):j]

