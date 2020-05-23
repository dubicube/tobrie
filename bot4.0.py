#sudo apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev
#pip install python-telegram-bot==12.0.0b1 --upgrade

from uuid import uuid4
import telegram
from telegram import InlineQueryResultArticle, InlineQueryResultVideo, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import re
import logging
import random
from datetime import datetime, timedelta
import time
import os
import requests
from timeloop import Timeloop
from zalgo_text import zalgo
import urllib.parse
import urllib.request

import re
from collections import defaultdict

import threading

from web_texts import *
from inventory import *
from audio import *

TEST = False

#videoPath = 'video/'
soundPath = 'sound/'
memePath = 'meme/'
logPath = 'log/'
tempPath = 'temp/'
dataServerAddress = 'http://copperbot.fr/tobrie_uploader/videos/'
thumbnailsServerAddress = 'http://copperbot.fr/tobrie_uploader/thumbnails/'



regex_start = "(^| |\')("
regex_end = ")($| |,|\\.|!|\\?)"

stickers_map_file = 'maps/sticker_map'
sticker_map_regex = []
text_map_file = 'maps/text_map'
text_map_regex = []
video_map_file = 'maps/video_map'
video_map_regex = []

dataPath = 'data/old/'

chatbot_enable = False
auto_reply = True
di_enable = True

users = {'Alban':470589955, 'Mathieu':400322253, 'Vincent':479998987,
        'Emile':938620840, 'Tristan':427032387, 'Leo':936261629,
        'Erwann':893891596, 'Sebastien':902796168, 'Hugo':460908392,
        'Martin':955908707}

admin_user_id = [users['Alban'], users['Vincent']]
super_admin = users['Vincent']

messages_perso = [['TudorEustache', 100, "C'est Ambre qui t'a dit ça?"],['lgqsbdc', 200, "Mais oui c'est clair!"],['G_W_did_911', 20, "C'est pas faux"],['Filipouq',10,"Je sais où tu te caches!"]]


id_test = -1001486633512
id_conv_robot = -1001455757279
id_campagne = -1001445559004
id_petites_loutres = -1001216704238
id_loutres_officielles = -1001403402459
id_first_year = -366419257

def id_print(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Campagne: "+str(id_campagne)+"\nPetites Loutres: "+str(id_petites_loutres)+"\nConv 1A: "+str(id_first_year))

conv_link = []#[id_loutres_officielles, id_first_year]

id_console = 479998987

conv_perso = 479998987
conv_out = conv_perso

depth = 0

########################################################################################################################################################
#                                                                       LOGS                                                                           #
########################################################################################################################################################

def saveToLog(msg):
    if not TEST:
        file = open(logPath+str(msg.chat_id),"a")
        file.write("["+msg.from_user.first_name+", "+str(msg.from_user.id)+", "+str(datetime.now())+": "+msg.text+"\n")
        file.close()

def notifConsole(update, context):
    message = getUpdateMessage(update)
    if message is None:return
    if (message.chat_id != (-1001455757279)):
        context.bot.send_message(chat_id=conv_perso, text="["+str(message.chat_id)+", "+message.from_user.first_name+", "+str(message.from_user.id)+": "+message.text)


########################################################################################################################################################
#                                                                       TEXT                                                                           #
########################################################################################################################################################

def removeAccents(text):
    return text.replace('é', 'e').replace('è', 'e')

def getUpdateMessage(update):
    if not update.message is None:
        return update.message
    if not update.edited_message is None:
        return update.edited_message
    return None

def sendVideo(message, context, file):
    context.bot.send_video(chat_id=message.chat_id, video=dataServerAddress+file, supports_streaming=True)

def sendYesNo(bot, message):
    if random.randint(0, 1) == 0:
        bot.sendChatAction(chat_id=message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
        bot.sendDocument(chat_id=message.chat_id, document="https://media1.giphy.com/media/uXiGkGqG4ZQ6A/giphy.gif?cid=3640f6095c9b5bc04c6d737836068cde")
    else:
        bot.sendChatAction(chat_id=message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
        bot.sendDocument(chat_id=message.chat_id, document="https://i.imgflip.com/19nqxs.gif")
def recur(message, context, msg):
    msg_lower = msg.lower()

    # Anti spam
    global depth
    depth+=1
    if depth > 2:return

    # di/cri
    regex_r = re.search('(?<=di)\\w{3,}', msg_lower)
    if regex_r != None:
        txt_rep = regex_r.group(0)
        context.bot.send_message(chat_id=message.chat_id, text=txt_rep)
        recur(message, context, txt_rep)
    regex_r = re.search('(?<=cri)\\w{3,}', msg_lower)
    if regex_r != None:
        txt_rep = regex_r.group(0)
        context.bot.send_message(chat_id=message.chat_id, text=txt_rep.upper())
        recur(message, context, txt_rep.upper())

    if "ariane" in msg_lower:
        context.bot.sendChatAction(chat_id=message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
        context.bot.sendDocument(chat_id=message.chat_id, document="https://media3.giphy.com/media/3ov9jPjweggTGwtalG/giphy.gif")

    if msg[-1] == "?" and random.randint(0, 2) == 0:
        if "qui" in msg:
            context.bot.send_message(chat_id=message.chat_id, text="C'est pas moi")
        else:
            sendYesNo(context.bot, message)


def handleText(update, context):
    #message = getUpdateMessage(update) # message source for regulat messages and for edited messages
    message = update.message # only regular messages (no update on edited messages)

    if message is None:
        return

    msg = message.text

    # Log + forward
    if message.chat_id != message.from_user.id:
        saveToLog(message);
    if message.chat_id == conv_perso:
        context.bot.send_message(chat_id=conv_out, text=update.message.text)
    else:
        notifConsole(update, context)

    # Auto response from google. Terminate if response provided
    if msg.lower()[0:7] == "brenda ":
        googleresp = getGoogleResponse(message.text[7:])
        if len(googleresp) > 1:
            context.bot.send_message(chat_id=message.chat_id, text=googleresp)
            return

    # Process text for responses
    if di_enable:
        global depth
        depth = 0
        for i in messages_perso:
            if message.from_user.username == i[0] and i[1]-1 >= 0 and random.randint(0, i[1]-1) == 0:
                context.bot.send_message(chat_id=message.chat_id, text=i[2])
        recur(message, context, msg)

    # Video auto reply
    if auto_reply:
        check_for_stickers(update, context, msg)
        check_for_text(update, context, msg)
        results = []
        i = 0
        msg = removeAccents(msg.lower())
        for s in video_map_regex:
            if not(re.search(regex_start+s[0]+regex_end, msg) is None):
                results+=[s[1]]
        if len(results) > 0:
            for i in range(len(results)):
                urllib.request.urlretrieve(dataServerAddress+results[0], tempPath+'temp'+str(i)+'.mp4')
            #open(tempPath+'vid0.mp4', 'wb').write(requests.get(dataServerAddress+results[0], allow_redirects=True).content)
            sendVideo(message, context, results[random.randint(0, len(results)-1)])

########################################################################################################################################################
#                                                                     REGEX MAPS                                                                       #
########################################################################################################################################################

def load_maps():
    global sticker_map_regex
    global text_map_regex
    global video_map_regex
    sticker_map_regex = []
    for l in open(stickers_map_file, "r").read().split('\n'):
        if len(l) > 2:
            a = l.index(' ')
            b = l.index(' ', a+1)
            sticker_map_regex+=[[l[:a], l[a+1:b], l[b+1:]]]
    #sticker_map_regex=[i.split('\n') for i in open(stickers_map_file, "r").read().split('\n\n')]
    text_map_regex=[i.split('\n') for i in open(text_map_file, "r").read().split('\n\n')]
    video_map_regex=[i.split('\n') for i in open(video_map_file, "r").read().split('\n\n')]
    video_map_regex = [[removeAccents(i[0]), i[1]] for i in video_map_regex]
load_maps()

def check_for_stickers(update, context, msg):
    for s in sticker_map_regex:
        if not(re.search(regex_start+s[2]+regex_end, msg.lower()) is None):
            if s[0] == "GIF":
                context.bot.send_animation(chat_id=update.message.chat_id, animation=s[1])
            elif s[0] == "FILE":
                context.bot.send_document(chat_id=update.message.chat_id, document=open(s[1], 'rb'))
            else:
                pack = context.bot.get_sticker_set(s[0])
                context.bot.sendSticker(chat_id=update.message.chat_id, sticker=pack.stickers[int(s[1])])

def check_for_text(update, context, msg):
    for s in text_map_regex:
        if not(re.search(s[0], msg.lower()) is None):
            context.bot.send_message(chat_id=update.message.chat_id, text=s[1])

########################################################################################################################################################
#                                                                       VIDEO                                                                          #
########################################################################################################################################################

video_names_out = []
def update_video_names():
    global video_names_out
    #Mouhahaha
    video_names_out=sorted([i.split('>')[0][9:-1] for i in urllib.parse.unquote(requests.get(dataServerAddress).text).split("<img src=\"/__ovh_icons/movie.gif\" alt=\"[VID]\"> ")[1:]])
update_video_names()
def update_video_names_command(update, context):
    load_maps()
    context.bot.send_message(chat_id=update.message.chat_id, text="Sticker map mise à jour ("+str(len(sticker_map_regex))+" stickers)")
    context.bot.send_message(chat_id=update.message.chat_id, text="Text map mise à jour ("+str(len(text_map_regex))+" textes)")
    context.bot.send_message(chat_id=update.message.chat_id, text="Video map mise à jour ("+str(len(video_map_regex))+" vidéos)")
    update_video_names()
    global video_names_out
    context.bot.send_message(chat_id=update.message.chat_id, text="Vidéos mises à jours ("+str(len(video_names_out))+" vidéos).")

def getResults(txt, names, nbr_max):
    results = []
    nbr = 0
    for vid in names:
        if nbr < nbr_max:
            i = 0
            ok = True
            while i < len(txt):
                if not(txt[i] in vid.lower()):
                    ok = False
                    i = len(txt)
                i+=1
            if ok:
                results+=[vid]
                nbr+=1
    return results
def inlinequery(update, context):
    context.bot.send_message(chat_id=conv_perso, text="["+", "+str(update.inline_query.from_user.first_name)+", "+str(update.inline_query.from_user.id)+": "+update.inline_query.query)
    txt = update.inline_query.query.lower().split(" ")

    if txt[0] == 'z':
        zal = zalgo.zalgo().zalgofy(" ".join(txt[1:]))
        results = [InlineQueryResultArticle(id=uuid4(), title=zal, input_message_content=InputTextMessageContent(zal), description=zal)]#zalgo.zalgo().zalgofy("Some text to zalgofy!")
        update.inline_query.answer(results)
    else:
        r = getResults(txt, video_names_out, 50)
        results = [InlineQueryResultVideo(uuid4(), dataServerAddress+vname.replace(" ", "%20"), "video/mp4", thumbnailsServerAddress+vname[:-3].replace(" ", "%20")+'jpg', vname) for vname in r]
        update.inline_query.answer(results)
def list(update, context):
    notifConsole(update, context)
    if update.message.chat_id == update.message.from_user.id:
        list_out = video_names_out
        if len(update.message.text) > 6:
            list_out = getResults(update.message.text[6:].lower().split(' '), video_names_out, 9999999)
        for i in range(len(list_out)//10):
            context.bot.send_message(chat_id=update.message.chat_id, text="\n".join(list_out[i*10:(i+1)*10]))
        context.bot.send_message(chat_id=update.message.chat_id, text="\n".join(list_out[(int(len(list_out)//10))*10:]))
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Le /list est interdit dans les groupes")
def dico(update, context):
    notifConsole(update, context)
    if update.message.chat_id == update.message.from_user.id:
        d = []
        for name in video_names_out:
            for i in name[:-4].split('_'):
                if not i in d:
                    d+=[i]
        d = sorted(d)
        for i in range(len(d)//100):
            context.bot.send_message(chat_id=update.message.chat_id, text=", ".join(d[i*100:(i+1)*100]))
        context.bot.send_message(chat_id=update.message.chat_id, text=", ".join(d[(int(len(d)//100))*100:]))
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Le /dico est interdit dans les groupes")

########################################################################################################################################################
#                                                              AUDIO                                                                                   #
########################################################################################################################################################

def calc(update, context):
    notifConsole(update, context)
    context.bot.send_chat_action(update.message.chat_id, 'upload_audio')
    calculate(update.message.text[6:], soundPath)
    context.bot.send_audio(chat_id=update.message.chat_id, audio=open(soundPath+"v.mp3", 'rb'))

def croa(update, context):
    notifConsole(update, context)
    context.bot.send_chat_action(update.message.chat_id, 'upload_audio')
    v = 1
    if len(update.message.text[6:]) > 0 and int(update.message.text[6:]) < 100:
        v = int(update.message.text[6:])
    duplicateAudio(soundPath+"croa"+".wav", soundPath+"v.wav", v)
    context.bot.send_audio(chat_id=update.message.chat_id, audio=open(soundPath+"v.mp3", 'rb'))


########################################################################################################################################################
#                                                              OTHER COMMANDS                                                                          #
########################################################################################################################################################

def conv(update, context):
    global conv_out
    if update.message.from_user.id == super_admin:
        conv_out = int(update.message.text[6:])
def setDI(update, context):
    notifConsole(update, context)
    #if update.message.from_user.id == super_admin:
    global di_enable
    di_enable = not(di_enable)
    context.bot.send_message(chat_id=update.message.chat_id, text=str(di_enable))
def setAutoReply(update, context):
    notifConsole(update, context)
    #if update.message.from_user.id == super_admin:
    global auto_reply
    auto_reply = not(auto_reply)
    context.bot.send_message(chat_id=update.message.chat_id, text=str(auto_reply))

def meme(update, context):
    notifConsole(update, context)
    memes = [f for f in os.listdir(memePath) if os.path.isfile(os.path.join(memePath, f))]
    m = memes[random.randint(0, len(memes)-1)]
    context.bot.send_photo(update.message.chat_id, open(memePath+m, 'rb'))

def help(update, context):
    notifConsole(update, context)
    context.bot.send_message(chat_id=update.message.chat_id, text=open("help.txt", "r").read())


########################################################################################################################################################
#                                                                TEXTS FROM WEB                                                                        #
########################################################################################################################################################

# Special function to send info/quote to another conversation and/or to spam it
def sendMessage(update, context, fun):
    param = chat_id=update.message.text.split(' ')
    ci = update.message.chat_id
    if len(param) >= 2:
        a = int(param[1])
        if a != 0:
            ci = a
    n = 1
    if len(param) >= 3:
        n = int(param[2])
    troll = n > 10
    if len(param) >= 4:
        troll = param[3]!="false"
    remove_l = []
    for i in range(n):
        m = context.bot.send_message(chat_id=ci, text=fun())
        if troll:
            remove_l = remove_l+[m.message_id]
    for id in remove_l:
        context.bot.delete_message(ci, id)
    if troll:
        context.bot.send_video(chat_id=ci, video=dataServerAddress+"nounours_en_fait_non.mp4", supports_streaming=True)
def info(update, context):
    notifConsole(update, context)
    sendMessage(update, context, getInfo)
def quote(update, context):
    notifConsole(update, context)
    sendMessage(update, context, getQuote)

########################################################################################################################################################
#                                                              OTHER COMMANDS                                                                          #
########################################################################################################################################################

def rapport(update, context):
    msg = update.message
    today = datetime.now()
    d = datetime(2020, 2, 12, 23, 59, 59, 999999)
    reste = d-today
    sec = reste.seconds
    if reste.days >= 0 and sec//3600>=0 and ((sec%3600)//60)>=0 and (sec%3600)%60>=0:
        context.bot.send_message(chat_id=msg.chat_id, text="Dépêche toi, il te reste "+str(reste.days)+" jours, "+str(sec//3600)+" heures, "+str((sec%3600)//60)+" minutes et "+str((sec%3600)%60)+" secondes pour finir ton rapport !")
    else:
        reste = today-d
        sec = reste.seconds
        context.bot.send_message(chat_id=msg.chat_id, text="Trop tard, il fallait rendre le rapport de projet robot il y a "+str(reste.days)+" jours, "+str(sec//3600)+" heures, "+str((sec%3600)//60)+" minutes et "+str((sec%3600)%60)+" secondes !")
        #context.bot.send_message(chat_id=msg.chat_id, text="C'est finiiiiiiiit!!!!!!")

########################################################################################################################################################
#                                                                    CHATBOT                                                                           #
########################################################################################################################################################
"""
def getDataFiles():
    return [dataPath+f for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath, f))]

class LString:
    def __init__(self):
        self._total = 0
        self._successors = defaultdict(int)

    def put(self, word):
        self._successors[word] += 1
        self._total += 1

    def get_random(self):
        ran = random.randint(0, self._total - 1)
        for key, value in self._successors.items():
            if ran < value:
                return key
            else:
                ran -= value

couple_words = defaultdict(LString)

def load(phrasesFiles):
    global couple_words
    couple_words = defaultdict(LString)
    for phrases in phrasesFiles:
        with open(phrases, 'r', encoding="utf8") as f:
            for line in f:
                #if line[0] == '[':
                #    line = line.split(':')[3]
                #    #message = re.sub(r'[^\w\s\']', '', line).lower().strip()
                #    #print(message)
                #    add_message(line)
                add_message(line)

def add_message(message):
    message = re.sub(r'[^\w\s\']', '', message).lower().strip()
    words = message.split()
    if len(words) < 2:
        return
    for i in range(2, len(words)):
        couple_words[(words[i - 2], words[i - 1])].put(words[i])
    couple_words[(words[-2], words[-1])].put("")

def generate():
    result = []
    while len(result) < 7 or len(result) > 20:
        result = []
        l = [i for i in couple_words.keys()]
        s = random.choice(l)
        result.extend(s)
        while result[-1]:
            w = couple_words[(result[-2], result[-1])].get_random()
            result.append(w)
    return " ".join(result)

def setChat(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=generate().replace('apos', '\''))
    #notifConsole(update, context)
    #if update.message.from_user.id == super_admin:
    #global chatbot_enable
    #chatbot_enable = not(chatbot_enable)
    #context.bot.send_message(chat_id=update.message.chat_id, text=str(chatbot_enable))

def loadData(update, context):
    load(getDataFiles())
load(getDataFiles())
"""

########################################################################################################################################################
#                                                                       INVENTORY                                                                      #
########################################################################################################################################################

inventory = []
if not(TEST):
    inventory = processInventoryHTML("base.html")
def find(update, context):
    results = searchInventory(update.message.text[6:], inventory)
    if len(results) < 10:
        for l in results:
            context.bot.send_message(update.message.chat_id, (("Référence: "+l[0]+"\n")if l[0]!=""else"")+("Nom: "+l[1]+"\n"if l[1]!=""else"")+("Emplacement: "+l[2]+"\n"if l[2]!=""else"")+("Caractéristique: "+l[3]if l[3]!=""else""))
    else:
        context.bot.send_message(update.message.chat_id, "Trop de résultats")

########################################################################################################################################################
#                                                                       MAIN                                                                           #
########################################################################################################################################################

tokens = open("tokens", "r").read().split("\n")
TOKEN=tokens[2] if TEST else tokens[0]
updater = Updater(TOKEN, use_context=True)

def shutdown():
    updater.stop()
    updater.is_idle = False
def stop(update, context):
    if update.message.from_user.id == super_admin:
        context.bot.send_message(update.message.chat_id, "Stopping...")
        threading.Thread(target=shutdown).start()


def main():
    dp = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    dp.add_handler(MessageHandler(Filters.text, handleText))
    dp.add_handler(InlineQueryHandler(inlinequery))
    #dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(CommandHandler('list',list))
    dp.add_handler(CommandHandler('dico',dico))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(CommandHandler('calc',calc))
    dp.add_handler(CommandHandler('meme',meme))
    dp.add_handler(CommandHandler('info',info))
    dp.add_handler(CommandHandler('quote',quote))
    dp.add_handler(CommandHandler('id',id_print))
    dp.add_handler(CommandHandler('di', setDI))
    dp.add_handler(CommandHandler('video', setAutoReply))
    dp.add_handler(CommandHandler('rapport',rapport))
    dp.add_handler(CommandHandler('update',update_video_names_command))
    dp.add_handler(CommandHandler('croa',croa))
    dp.add_handler(CommandHandler('find',find))

    #dp.add_handler(CommandHandler('chat',setChat))
    #dp.add_handler(CommandHandler('loadData',loadData))


    #Personal commands
    dp.add_handler(CommandHandler('conv', conv))
    dp.add_handler(CommandHandler('stop', stop))

    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()
