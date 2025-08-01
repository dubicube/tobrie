import re
import random
from config import *
from shared_core import *
from generic.web_texts import getGoogleResponse
from contextual_bot import ContextualBot
from gpt import *

from generic.dateFuns import *


messages_perso = [
    # ['TudorEustache', 100, "C'est Ambre qui t'a dit ça?"]
]

conv_out = conv_perso
depth = 0 # Recusrsivity meter


async def configureParameters(contextual_bot, sh_core):
    parameters = sh_core.getParameterList().getConv(contextual_bot.getChatID())
    t = contextual_bot.getText().split(' ')
    #v = not parameters.getBoolean("DI_ENABLE")
    if len(t) == 5:
        parameters.setBoolean("AUTOREPLY_ENABLE", t[1])
        parameters.setBoolean("TEXT_ENABLE", t[2])
        parameters.setBoolean("STICKER_ENABLE", t[3])
        parameters.setBoolean("VIDEO_ENABLE", t[4])

    reply = ""
    reply+="Auto reply: "+str(parameters.getBoolean("AUTOREPLY_ENABLE"))+"\n"
    reply+="Text: "+str(parameters.getBoolean("TEXT_ENABLE"))+"\n"
    reply+="Stickers: "+str(parameters.getBoolean("STICKER_ENABLE"))+"\n"
    reply+="Videos: "+str(parameters.getBoolean("VIDEO_ENABLE"))+"\n"
    await sh_core.notifConsole(contextual_bot)
    contextual_bot.reply(ContextualBot.TEXT, reply)

async def configureProba(contextual_bot, sh_core):
    parameters = sh_core.getParameterList().getConv(contextual_bot.getChatID())
    t = contextual_bot.getText().split(' ')
    #v = not parameters.getBoolean("DI_ENABLE")

    errorMsg = False

    if len(t) == 5:
        prob = parameters.getList("PROBAS")
        t = t[1:]
        for i in range(len(t)):
            v = -1
            try:
                v = int(t[i])
            except:
                v = int(prob[i])
            if v >= 0 and v <= 100:
                prob[i] = str(v)
        parameters.setList("PROBAS", prob)
    elif len(t) == 2:
        prob = parameters.getList("PROBAS")
        v = -1
        try:
            v = int(t[1])
        except:
            v = int(prob[0])
        if v >= 0 and v <= 100:
            prob = [str(v) for _ in range(4)]
        parameters.setList("PROBAS", prob)
    elif len(t) != 1:
        errorMsg = True

    if errorMsg:
        contextual_bot.reply(ContextualBot.TEXT, "Ptdr tu sais pas utiliser la commande\nIl faut 1 ou 4 paramètres entre 0 et 100")
    else:
        prob = parameters.getList("PROBAS")
        reply = ""
        reply+="Auto reply: "+prob[0]+"\n"
        reply+="Text: "+prob[1]+"\n"
        reply+="Stickers: "+prob[2]+"\n"
        reply+="Videos: "+prob[3]+"\n"
        await sh_core.notifConsole(contextual_bot)
        contextual_bot.reply(ContextualBot.TEXT, reply)

def conv(contextual_bot):
    global conv_out
    if contextual_bot.getUserID() == super_admin:
        conv_out = int(contextual_bot.getText()[6:])
async def setAutoReplyOn(contextual_bot, sh_core):
    parameters = sh_core.getParameterList().getConv(contextual_bot.getChatID())
    parameters.setBoolean("AUTOREPLY_ENABLE", True)
    await sh_core.notifConsole(contextual_bot)
async def setAutoReplyOff(contextual_bot, sh_core):
    parameters = sh_core.getParameterList().getConv(contextual_bot.getChatID())
    parameters.setBoolean("AUTOREPLY_ENABLE", False)
    await sh_core.notifConsole(contextual_bot)

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
    regex_r = re.search('(?<=d((i|î|í|ì)|y))\\w{3,}', msg_lower)
    if regex_r != None:
        txt_rep = regex_r.group(0)
        contextual_bot.reply(ContextualBot.TEXT, txt_rep)
        recur(contextual_bot, txt_rep, level)
    regex_r = re.search('(?<=cr(i|î|í|ì))\\w{3,}', msg_lower)
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

async def handleText(contextual_bot, sh_core, level=0):
    parameters = sh_core.getParameterList().getConv(contextual_bot.getChatID())
    if len(contextual_bot.getAbsoluteText()) == 0:
        return

    msg = contextual_bot.getText()

    # Log + forward
    #if not contextual_bot.isChatPerso():
    #    sh_core.saveToLog(contextual_bot);
    if contextual_bot.getChatID() == conv_perso:
        await sh_core.telegramBot.send_message(chat_id=conv_out, text=contextual_bot.getText())
    else:
        await sh_core.notifConsole(contextual_bot)

    # Auto response from chatgpt. Terminate if response provided
    # (Actually no longer working..........)
    chatgpt_resp = GPT_getResponse(contextual_bot)
    if len(chatgpt_resp) > 1:
        contextual_bot.reply(ContextualBot.TEXT, chatgpt_resp)
        return


    #================================================
    # Achievements
    #================================================
    dataManager = data_manager.DataManager()

    # Achievement long message
    maxMessageLength = dataManager.getRessource(contextual_bot.getChatID(), "maxMessageLength")
    if len(maxMessageLength) == 0 or len(msg) > int(maxMessageLength):
        dataManager.saveRessource(contextual_bot.getChatID(), "maxMessageLength", str(len(msg)))
        contextual_bot.addAchievement(contextual_bot.TEXT, "Achievement unlocked: message le plus long dans la conversation: " + str(len(msg)) + " caractères")

    # Achievement last message date
    lastMessageDates = dataManager.getRessource(contextual_bot.getChatID(), "lastMessageDates")
    lastMessageDates = [i.split('$') for i in lastMessageDates.split(',') if len(i) > 0]
    if len(lastMessageDates) == 0:
        lastMessageDates = [["0"]]
    maxDuration = float(lastMessageDates[0][0])
    lastMessageDates = [[int(i[0]), i[1]] for i in lastMessageDates[1:]]
    idIndex = -1
    for i in range(len(lastMessageDates)):
        if lastMessageDates[i][0] == contextual_bot.getUserID():
            idIndex = i
            break
    now = datetime.today()
    if idIndex == -1:
        lastMessageDates += [[contextual_bot.getUserID(), str(now)]]
        idIndex = len(lastMessageDates) - 1
    delta_s = (now-datetime.strptime(lastMessageDates[idIndex][1], "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
    lastMessageDates[idIndex][1] = str(now)

    # Check if achievement should be unlocked
    if delta_s > maxDuration:
        maxDuration = delta_s
        (days, hours, minutes, seconds) = getDHMS(delta_s)
        contextual_bot.addAchievement(contextual_bot.TEXT, "Achievement unlocked: plus long temps depuis le dernier message de " + smartDayPrintStr(days, hours, minutes, seconds))

    # Pack all data to a single string before saving it with the data manager
    lastMessageDates = [str(maxDuration)] + [str(i[0])+'$'+str(i[1]) for i in lastMessageDates]
    lastMessageDates = ','.join(lastMessageDates)
    dataManager.saveRessource(contextual_bot.getChatID(), "lastMessageDates", lastMessageDates)





    if parameters.getBoolean("AUTOREPLY_ENABLE") and random.randint(1, 100) <= int(parameters.getList("PROBAS")[0]):

        if parameters.getBoolean("TEXT_ENABLE") and random.randint(1, 100) <= int(parameters.getList("PROBAS")[1]):
            global depth
            depth = 0
            for i in messages_perso:
                if contextual_bot.getUserName() == i[0] and i[1]-1 >= 0 and random.randint(0, i[1]-1) == 0:
                    contextual_bot.reply(ContextualBot.TEXT, i[2])
            recur(contextual_bot, msg, level)
            check_for_text(contextual_bot, msg)
        if parameters.getBoolean("STICKER_ENABLE") and random.randint(1, 100) <= int(parameters.getList("PROBAS")[2]):
            check_for_stickers(contextual_bot, sh_core, msg)
        if parameters.getBoolean("VIDEO_ENABLE") and random.randint(1, 100) <= int(parameters.getList("PROBAS")[3]):
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
            if l[a+1] == '@':
                c = l.index(' ', b+1)
                sticker_map_regex+=[[l[:a], l[b+1:c], l[c+1:], int(l[a+2:b])]]
            else:
                sticker_map_regex+=[[l[:a], l[a+1:b], l[b+1:], 100]]
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
    #if len(results) > 0:
    for s in results:
        #s = results[random.randint(0, len(results)-1)]
        if s[0] == "GIF":
            contextual_bot.reply(ContextualBot.ANIMATION, s[1], s[3])
        elif s[0] == "FILE":
            contextual_bot.reply(ContextualBot.DOCUMENT, open(s[1], 'rb'), s[3])
        elif s[0] == "IMAGE":
            contextual_bot.reply(ContextualBot.IMAGE, open(s[1], 'rb'), s[3])
        else:
            pack = sh_core.telegramBot.get_sticker_set(s[0])
            if '~' in s[1]:
                l = s[1].split('~')
                contextual_bot.reply(ContextualBot.STICKER, pack.stickers[random.randint(int(l[0]), int(l[1]))], s[3])
            else:
                contextual_bot.reply(ContextualBot.CHAINED_STICKERS, [pack.stickers[int(index)] for index in s[1].split(',')], s[3])

def check_for_text(contextual_bot, msg):
    for s in text_map_regex:
        if not(re.search(s[0], msg.lower()) is None):
            contextual_bot.reply(ContextualBot.TEXT, s[1])

def getRandomVideoURL():
    global video_map_regex
    if len(video_map_regex) == 0:
        return None
    return dataServerAddress + video_map_regex[random.randint(0, len(video_map_regex)-1)][1]
