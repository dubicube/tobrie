from config import *
from contextual_bot import *

def FLM_getFile(contextual_bot, sh_core, fileName):
    data = open(mapPath+fileName, "r").read()
    if len(data.split('\n')) < 10:
        contextual_bot.reply(ContextualBot.TEXT, data)
    else:
        contextual_bot.reply(ContextualBot.DOCUMENT, open(mapPath+fileName, 'rb'))

def FLM_addLine(contextual_bot, sh_core, fileName):
    txt = contextual_bot.getText()
    i = 0
    while (i+1 < len(txt) and txt[i] != ' '):
        i+=1
    txt = txt[i+1:].split('\n')[0]
    reply = contextual_bot.getReplyText()
    if len(reply) > 1:
        # Yeah baby, add a space
        txt = reply + " " + txt
    # Yeah baby, send the message only when it is longer than 1
    if len(txt) > 1:
        f = open(mapPath+fileName, "a")
        f.write(txt.strip("\n")+"\n")
        f.close()
        contextual_bot.reply(ContextualBot.TEXT, "Ok")
    else:
        # Yeah baby, this code is executed when the dumb user do something stupid
        contextual_bot.reply(ContextualBot.TEXT, "Ptdr tu sais pas utiliser la commande")

# Yeah baby, adding "yeah baby" is strange and the guy reading this will ask so many questions about the guy who wrote that shitty code, but, yeah baby, it works !
