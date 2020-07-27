import re
import random
from config import *
from shared_core import *
from web_texts import getGoogleResponse
from contextual_bot import ContextualBot

messages_perso = [
    ['TudorEustache', 100, "C'est Ambre qui t'a dit ça?"],
    ['dicribolzano', 200, "Mais oui c'est clair!"],
    ['G_W_did_911', 20, "C'est pas faux"],
    ['Filipouq',10,"Je sais où tu te caches!"]
]

conv_out = conv_perso
depth = 0 # Recusrsivity meter
di_enable = True
auto_reply = True


def setDI(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    global di_enable
    di_enable = not(di_enable)
    contextual_bot.reply(ContextualBot.TEXT, str(di_enable))
def conv(contextual_bot):
    global conv_out
    if contextual_bot.getUserID() == super_admin:
        conv_out = int(contextual_bot.getText()[6:])
def setAutoReply(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    global auto_reply
    auto_reply = not(auto_reply)
    contextual_bot.reply(ContextualBot.TEXT, str(auto_reply))

def removeAccents(text):
    return text.replace('é', 'e').replace('è', 'e')

def sendYesNo(contextual_bot):
    if random.randint(0, 1) == 0:
        contextual_bot.reply(ContextualBot.VIDEO, dataServerAddress+"non.mp4")
    else:
        contextual_bot.reply(ContextualBot.VIDEO, dataServerAddress+"oui.mp4")

def recur(contextual_bot, msg, level):
    msg_lower = msg.lower()

    # Anti spam
    global depth
    depth+=1
    if depth > 2:return

    # di/cri
    regex_r = re.search('(?<=di)\\w{3,}', msg_lower)
    if regex_r != None:
        txt_rep = regex_r.group(0)
        contextual_bot.reply(ContextualBot.TEXT, txt_rep)
        recur(contextual_bot, txt_rep, level)
    regex_r = re.search('(?<=cri)\\w{3,}', msg_lower)
    if regex_r != None:
        txt_rep = regex_r.group(0)
        contextual_bot.reply(ContextualBot.TEXT, txt_rep.upper())
        recur(contextual_bot, txt_rep.upper(), level)
    regex_r = re.search('\\w{1,}ines?(?!\\w)', msg_lower)
    if regex_r != None:
        txt_rep = regex_r.group(0)
        txt_rep = txt_rep[:-3-(txt_rep[-1]=='s')]
        contextual_bot.reply(ContextualBot.TEXT, "C'est pain au "+txt_rep+", pas "+txt_rep+"ine")
        recur(contextual_bot, txt_rep, level)

    if msg[-1] == "?" and random.randint(0, 2) == 0:
        if "qui" in msg:
            contextual_bot.reply(ContextualBot.TEXT, "C'est pas moi")
        else:
            sendYesNo(contextual_bot)

def handleText(contextual_bot, sh_core, level=0):
    if len(contextual_bot.getAbsoluteText()) == 0:
        return

    msg = contextual_bot.getText()

    # Log + forward
    #if not contextual_bot.isChatPerso():
    #    sh_core.saveToLog(contextual_bot);
    if contextual_bot.getChatID() == conv_perso:
        sh_core.telegramBot.send_message(chat_id=conv_out, text=contextual_bot.getText())
    else:
        sh_core.notifConsole(contextual_bot)

    # Auto response from google. Terminate if response provided
    if msg.lower()[0:7] == "brenda ":
        #googleresp = getGoogleResponse(msg[7:])
        googleresp = sh_core.remote_service.sendToClient(msg[7:])
        if len(googleresp) > 1:
            contextual_bot.reply(ContextualBot.TEXT, googleresp)
            return

    # Process text for responses
    if di_enable:
        global depth
        depth = 0
        for i in messages_perso:
            if contextual_bot.getUserName() == i[0] and i[1]-1 >= 0 and random.randint(0, i[1]-1) == 0:
                contextual_bot.reply(ContextualBot.TEXT, i[2])
        recur(contextual_bot, msg, level)

    # Video auto reply
    if auto_reply:
        check_for_stickers(contextual_bot, sh_core, msg)
        check_for_text(contextual_bot, msg)
        results = []
        i = 0
        msg = removeAccents(msg.lower())
        for s in video_map_regex:
            if not(re.search(regex_start+s[0]+regex_end, msg) is None):
                results+=[s[1]]
        if len(results) > 0:
            #for i in range(len(results)):
            #    urllib.request.urlretrieve(dataServerAddress+results[0], tempPath+'temp'+str(i)+'.mp4')
            #context.bot.send_video(chat_id=message.chat_id, video=dataServerAddress+results[random.randint(0, len(results)-1)], supports_streaming=True)
            contextual_bot.reply(ContextualBot.VIDEO, dataServerAddress+results[random.randint(0, len(results)-1)])

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

def check_for_stickers(contextual_bot, sh_core, msg):
    results = []
    for s in sticker_map_regex:
        if not(re.search(regex_start+s[2]+regex_end, msg.lower()) is None):
            results+=[s]
    if len(results) > 0:
        s = results[random.randint(0, len(results)-1)]
        if s[0] == "GIF":
            contextual_bot.reply(ContextualBot.ANIMATION, s[1])
        elif s[0] == "FILE":
            contextual_bot.reply(ContextualBot.DOCUMENT, open(s[1], 'rb'))
        elif s[0] == "IMAGE":
            contextual_bot.reply(ContextualBot.IMAGE, open(s[1], 'rb'))
        else:
            pack = sh_core.telegramBot.get_sticker_set(s[0])
            contextual_bot.reply(ContextualBot.STICKER, pack.stickers[int(s[1])])

def check_for_text(contextual_bot, msg):
    for s in text_map_regex:
        if not(re.search(s[0], msg.lower()) is None):
            contextual_bot.reply(ContextualBot.TEXT, s[1])
