import random
from config import *
from BridgeBot import *



def configureParameters(contextual_bot, sh_core):
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
    sh_core.notifConsole(contextual_bot)
    contextual_bot.reply(ContextualBot.TEXT, reply)

def configureProba(contextual_bot, sh_core):
    parameters = sh_core.getParameterList().getConv(contextual_bot.getChatID())
    t = contextual_bot.getText().split(' ')
    #v = not parameters.getBoolean("DI_ENABLE")
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

    prob = parameters.getList("PROBAS")
    reply = ""
    reply+="Auto reply: "+prob[0]+"\n"
    reply+="Text: "+prob[1]+"\n"
    reply+="Stickers: "+prob[2]+"\n"
    reply+="Videos: "+prob[3]+"\n"
    sh_core.notifConsole(contextual_bot)
    contextual_bot.reply(ContextualBot.TEXT, reply)



def filterReplies(replies):
    r = []
    if parameters.getBoolean("AUTOREPLY_ENABLE")
    and random.randint(1, 100) <= int(parameters.getList("PROBAS")[0]):
        repliesText = []
        repliesImage = []
        repliesFile = []
        for r in replies:
            if r.messageType == MessageType.TEXT:
                repliesText.append(r)
            elif r.messageType == MessageType.IMAGE
            or r.messageType == MessageType.VIDEO
            or r.messageType == MessageType.STICKER:
                repliesImage.append(r)
            elif r.messageType == MessageType.FILE:
                repliesFile.append(r)
        if len(repliesText) > 0:
            r.append(random.choice(repliesText))
        if len(repliesImage) > 0:
            r.append(random.choice(repliesImage))
        if len(repliesFile) > 0:
            r.append(random.choice(repliesFile))

    
    return r