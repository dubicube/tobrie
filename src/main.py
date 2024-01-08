import discord
from discord import FFmpegPCMAudio
from discord.utils import get

import tweepy

import openai

from credit_card_info_generator import generate_credit_card
import aspose.words as aw

from uuid import uuid4
import telegram
from telegram import InlineQueryResultArticle, InlineQueryResultVideo, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import re
import logging
import random
from datetime import datetime
import time
import os
import signal
import requests
from zalgo_text import zalgo
import urllib.parse
from urllib import request

import threading

from config import *
from contextual_bot import *
from shared_core import *
from gpt import *
from generic.web_texts import *
from eirbot.inventory import *
from generic.audio import *
from auto_reply import handleText, load_maps, configureParameters, configureProba, setAutoReplyOn, setAutoReplyOff, conv, handle_video
from generic.youtube import *
from generic.mail_manager import *
from service.brendapi import *
from service.remote_service_server import *
from file_list_manager import *
from generic.morse import MSR_cancer, MSR_config

import events_ui

sticker_map_regex = []
text_map_regex = []
video_map_regex = []

sh_core = None


#########################################################################################
#                                        PYBRENDA                                       #
#########################################################################################

import pexpect

HOST = "127.0.0.1"
PORT = 63913
pybrenda = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pybrenda.settimeout(0.2)
pybrenda_enabled = True
try:
    pybrenda.connect((HOST, PORT))
except:
    pybrenda_enabled = False
    print("Pybrenda not working")

def runPybrenda(command):
    r = ""
    try:
        pybrenda.sendall(command)
    except:
        return r
    while True:
        try:
            data = pybrenda.recv(1024)
            if len(data) == 0:
                # Pybrenda is not responding, thus we disable it
                # It will be re-enabled when the server is restarted
                pybrenda_enabled = False
                break
            r+=str(data)[2:-1]+"\n"
        except:
            break
    return r

def highLevelTextCallback(contextual_bot, sh_core):
    msg = contextual_bot.getText()
    rep = ""
    if pybrenda_enabled and (contextual_bot.getChatID() in [-1001168293232, -1001216704238, conv_perso, -1001459505391]):
        rep = runPybrenda(bytes(msg, 'utf8'))
        if "<function" in rep and len(msg.split(' ')) == 1:
            rep = runPybrenda(bytes(msg+"()", 'utf8'))

    if not("line 1" in rep and ("SyntaxError" in rep or "NameError" in rep)) and len(rep) > 0:
        sh_core.notifConsole(contextual_bot)
        sh_core.notifConsole(contextual_bot, rep)
        contextual_bot.reply(ContextualBot.TEXT, rep)
    else:
        handleText(contextual_bot, sh_core)

#########################################################################################
#                                        VIDEO                                          #
#########################################################################################

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
        results = [InlineQueryResultArticle(id=uuid4(), title=zal, input_message_content=InputTextMessageContent(zal), description=zal)]
        update.inline_query.answer(results)
    else:
        r = getResults(txt, video_names_out, 50)
        results = [InlineQueryResultVideo(uuid4(), dataServerAddress+vname.replace(" ", "%20"), "video/mp4", thumbnailsServerAddress+vname[:-3].replace(" ", "%20")+'jpg', vname) for vname in r]
        update.inline_query.answer(results)
def list(update, context):
    sh_core.notifConsole(TelegramBot(update, context))
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
    sh_core.notifConsole(TelegramBot(update, context))
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

#########################################################################################
#                                        AUDIO                                          #
#########################################################################################

def morse(contextual_bot, sh_core):
    cdata = contextual_bot.getText()[7:]
    # Get eventual audio file replying to
    fpath = contextual_bot.getReplyAudioFile()
    # Convert file to wav if format is mp3
    if fpath.endswith('.mp3'):
        convertAudioFile(fpath, tempPath + 'morse.wav')
        fpath = tempPath + 'morse.wav'
    # If we got a wav file, edit config, else, generate morse sound from text in message
    if fpath.endswith('.wav'):
        MSR_config(fpath, cdata)
        contextual_bot.reply(ContextualBot.TEXT, "Ok")
    else:
        fname = MSR_cancer(cdata)
        contextual_bot.reply(ContextualBot.AUDIO, open(fname, 'rb'))



def search_sound(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    data = contextual_bot.getText()[7:]
    n = data.split(' ')[-1]
    m = 0
    try:
        m = int(n)
        data = ' '.join(data.split(' ')[:-1])
    except Exception:
        m = 0
    if getSound(data, tempPath+'v.mp3', m):
        contextual_bot.reply(ContextualBot.AUDIO, open(tempPath+'v.mp3', 'rb'))
    else:
        contextual_bot.reply(ContextualBot.TEXT, "Rien trouvé (ou alors ça a planté)")

def calc(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    calculate(contextual_bot.getText()[6:], soundPath)
    contextual_bot.reply(ContextualBot.AUDIO, open(soundPath+"v.mp3", 'rb'))

def croa(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    v = 1
    txt = contextual_bot.getText()
    if len(txt[6:]) > 0 and int(txt[6:]) < 100:
        v = int(txt[6:])
    duplicateAudio(soundPath+"croa"+".wav", soundPath+"v.wav", v)
    contextual_bot.reply(ContextualBot.AUDIO, open(soundPath+"v.wav", 'rb'))
voiceLanguage = "fr-FR"
voiceSpeed = False
def sayText(contextual_bot, sh_core):
    getVoice(contextual_bot.getText()[5:], soundPath+'v.mp3', voiceLanguage)
    contextual_bot.reply(ContextualBot.AUDIO, open(soundPath+'v.mp3', 'rb'))
def sayText2(contextual_bot, sh_core):
    t = contextual_bot.getText()[5:].split(' ')
    tf = ""
    i = 0
    forcel = ""
    while i < len(t):
        if i+1 < len(t) and t[i] == '-l':
            forcel = t[i+1]
            i+=2
        else:
            tf+=t[i]+' '
            i+=1
    # if tf == "":
    #     tf = contextual_bot.getReplyText()
    vl = voiceLanguage
    if isValidLanguage(forcel) != "":
        vl = forcel
    getVoice2(tf, soundPath+'v.mp3', vl, voiceSpeed)
    contextual_bot.reply(ContextualBot.AUDIO, open(soundPath+'v.mp3', 'rb'))

def isValidLanguage(str):
    h = [i.split(": ") for i in getHelp("lang").split('\n')[5:-1]]
    value = [i[0] for i in h]
    text = [i[1] for i in h]
    if str in value:
        i = value.index(str)
        return text[i]
    else:
        return ""
def setVoiceLanguage(contextual_bot, sh_core):
    global voiceLanguage
    t = contextual_bot.getText()[6:]
    r = isValidLanguage(t)
    if r == "":
        contextual_bot.reply(ContextualBot.TEXT, "Language not found\nType \"/help lang\" for more information")
    else:
        voiceLanguage = t
        contextual_bot.reply(ContextualBot.TEXT, "Language selected:\n"+text[i])

def setVoiceSpeed(contextual_bot, sh_core):
    global voiceSpeed
    t = contextual_bot.getText()[7:]
    if t == '1':
        voiceSpeed = False
    elif t == '0':
        voiceSpeed = True
    else:
        contextual_bot.reply(ContextualBot.TEXT, "TOCARD ! T'es sensé mettre 0 ou 1 en paramètre !")


#########################################################################################
#                                   OTHER COMMANDS                                      #
#########################################################################################

def meme(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    memes = [f for f in os.listdir(memePath) if os.path.isfile(os.path.join(memePath, f))]
    m = memes[random.randint(0, len(memes)-1)]
    contextual_bot.reply(ContextualBot.IMAGE, open(memePath+m, 'rb'))

def getHelp(data):
    help_data_file = open("help.txt", "r")
    help_data = help_data_file.read().split('\n\n')
    help_data_file.close()
    if len(data) == 0:
        return help_data[0]
    else:
        param = data.lower()
        if param[0]=='/' or param[0]=='@':
            param = param[1:]
        i=0
        while i<len(help_data) and help_data[i].split('\n')[0].split(' ')[1].replace('/', '').replace('@', '') != param:
            i+=1
        if i<len(help_data):
            return help_data[i]
        else:
            return help_data[0]
def help(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    if len(contextual_bot.getText()) <= 7:
        contextual_bot.reply(ContextualBot.TEXT, getHelp(""))
    else:
        contextual_bot.reply(ContextualBot.TEXT, getHelp(contextual_bot.getText()[6:]))

def outputGenre(contextual_bot, sh_core):
    contextual_bot.reply(ContextualBot.TEXT, "Je suis un hélicoptère apache")

def outputPlaylists(contextual_bot, sh_core):
    txt = """
    Les playlists principales :

     - La playlist EIRBOT classique :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjGI_ZPwxH9uJIvjECZ1-pDA

     - La playlist EIRBOOM si vous voulez griller des enceintes :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjFRk9cEoq9tnNmJ_i1eqMqh

     - La playlist WEABOT, plutôt tourné japonais :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjHVbGcnf72N_nHPE8uPOJ9e


    Les playlists annexes :

     - La playlist NIGHTBOT, principalement du nightcore :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjHIyN61g-Luq4oUoS7qPGn6

     - La playlist TECHNOBOT (diffère de EIRBOOM) :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjE4Sg3zP4OUjWqqKYNJqH_c

     - La playlist EIRBROCK, bah c'est du rock :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjGGFueC0xDGqMQuTULrefK6

     - La playlist 50 BOT, rap & co :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjHYLJltciOHZ0aw3Mb2ib1Y

     - La playlist JAZZABOT, devine cé koi :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjFekFP-VjuaFOTF23rUawnJ

     - La playlist FUNKYBOT, c'est la founke :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjGYU1KvnRUb8xCtUMt1NHJT

     - La playlist HOUSEBOT, de la house :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjHCGVAtOX5OymyO-MIU6cGF

     - La playlist EPICBOT, des musiques epics :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjFfF0II3cyUK4A1aTQpgnYP

     - La playlist WEIRDBOT, les trucs chelou (musique ou clip) trouvés sur youtube :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjHFYSipulnliBNU7whFYcyO

     - La playlist TRASHBOT (dans le sens poubelle), un peu les bas fonds de youtube, parfois inécoutable :
    https://www.youtube.com/playlist?list=PLCQolDsR1jjECMSRIFQ4xT4e98J-YjDWt
    """
    contextual_bot.reply(ContextualBot.TEXT, txt)


def outputHoraires(contextual_bot, sh_core):
    contextual_bot.reply(ContextualBot.TEXT,
"""* 7h-22h du lundi au vendredi
* 8h-20h le samedi
* fermé le dimanche
Sachant que la sécu vire les gens environ 30min avant""")

def setWelcomeMessage(contextual_bot, sh_core):
    dm = data_manager.DataManager()
    text = contextual_bot.getReplyText()
    sticker = contextual_bot.getReplySticker()
    video = contextual_bot.getReplyVideo()
    print(video)
    success = True
    if text != "":
        dm.saveRessource(contextual_bot.getChatID(), "welcome", "T" + text)
    elif sticker != "":
        dm.saveRessource(contextual_bot.getChatID(), "welcome", "S" + sticker)
    elif video != "":
        dm.saveRessource(contextual_bot.getChatID(), "welcome", "V" + video)
    else:
        success = False
    if success:
        contextual_bot.reply(ContextualBot.TEXT, "OK")
    else:
        contextual_bot.reply(ContextualBot.TEXT, "Tocard, tu sais pas utiliser la commande.\nIl faut invoquer la commande en répondant à un message. Le message répondu sera le message automatiquement envoyé lors de l'arrivée d'une nouvelle personne. Seulement le texte, les stickers et les vidéos sont supportés.")


#########################################################################################
#                                   USELESS TEXTS                                       #
#########################################################################################

def info(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    contextual_bot.reply(ContextualBot.TEXT, getInfo())
def quote(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    contextual_bot.reply(ContextualBot.TEXT, getQuote())
def search_image(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    url = getGoogleImage(contextual_bot.getText()[5:])
    extension = url.split(".")[-1]
    if extension == "gif":
        contextual_bot.reply(ContextualBot.ANIMATION, url)
    else:
        image_name = tempPath+"out."+extension
        download_image(url, image_name)
        contextual_bot.reply(ContextualBot.IMAGE, open(image_name, "rb"))
def getAlie(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    #product = getFirstAlie(contextual_bot.getText()[5:])
    product = sh_core.remote_service.sendToClient('1'+contextual_bot.getText()[5:]).split('///')
    if len(product) != 2:
        contextual_bot.reply(ContextualBot.TEXT, "Connection failed")
        return
    url = product[1]
    extension = url.split(".")[-1]
    image_name = tempPath+"out."+extension
    download_image(url, image_name)
    contextual_bot.reply(ContextualBot.TEXT, product[0])
    contextual_bot.reply(ContextualBot.IMAGE, open(image_name, "rb"))

def porteMegane(contextual_bot, sh_core):
    today = datetime.today()
    f = open("./../maps/porte", "r")
    d = f.read()[:10]
    f.close()
    d = datetime.strptime(d, "%Y-%m-%d")
    delta = today - d
    contextual_bot.reply(ContextualBot.TEXT, "Nombre de jours depuis le dernier démontage de porte de Mégane: " + str(delta.days))

def bureauList(contextual_bot, sh_core):
    data = open(mapPath+"bureau", "r").read()
    contextual_bot.reply(contextual_bot.TEXT, data)

def pdfConvert(contextual_bot, sh_core):
    path = contextual_bot.downloadReplyDocument(tempPath)
    if path.endswith('docx'):
        doc = aw.Document(path)
        pdfPath = path[:-4] + 'pdf'
        doc.save(pdfPath)
        contextual_bot.reply(contextual_bot.DOCUMENT, open(pdfPath, 'rb'))
    else:
        contextual_bot.reply(contextual_bot.TEXT, "Fichier invalide")

def creditCard(contextual_bot, sh_core):
    card = generate_credit_card('Visa')
    contextual_bot.reply(contextual_bot.TEXT, "Number: " + str(card["card_number"]) + "\nCVV: " + str(card["cvv"]) + "\nExpiry date: " + str(card["expiry_date"]))

#########################################################################################
#                                       RAPPORT                                         #
#########################################################################################

def rapport(update, context):
    msg = update.message
    today = datetime.now()
    d = datetime(2020, 8, 27, 21, 59, 59, 999999)
    reste = d-today
    sec = reste.seconds
    if reste.days >= 0 and sec//3600>=0 and ((sec%3600)//60)>=0 and (sec%3600)%60>=0:
        context.bot.send_message(chat_id=msg.chat_id, text="Il reste "+str(reste.days)+" jours, "+str(sec//3600)+" heures, "+str((sec%3600)//60)+" minutes et "+str((sec%3600)%60)+" secondes pour finir le rapport (ou le commencer...)")
    else:

        context.bot.send_message(chat_id=msg.chat_id, text="Il reste "+str(sec//3600)+" heures, "+str((sec%3600)//60)+" minutes et "+str((sec%3600)%60)+" secondes pour finir le rapport avec "+str(24*-reste.days)+"h de retard")
        context.bot.send_animation(msg.chat_id, "https://tenor.com/view/fine-this-is-fine-fine-dog-shaking-intensifies-im-ok-gif-15733726")
        #reste = today-d
        #sec = reste.seconds
        #context.bot.send_message(chat_id=msg.chat_id, text="Trop tard, il fallait rendre le rapport il y a "+str(reste.days)+" jours, "+str(sec//3600)+" heures, "+str((sec%3600)//60)+" minutes et "+str((sec%3600)%60)+" secondes !")
        #context.bot.send_message(chat_id=msg.chat_id, text="C'est finiiiiiiiit!!!!!!")

#########################################################################################
#                                      INVENTORY                                        #
#########################################################################################

inventory = []
if not(TEST):
    inventory = processInventoryHTML("eirbot/base.html")
def find(contextual_bot, sh_core):
    results = searchInventory(contextual_bot.getText()[6:], inventory)
    if len(results) < 10:
        for l in results:
            contextual_bot.reply(ContextualBot.TEXT, (("Référence: "+l[0]+"\n")if l[0]!=""else"")+("Nom: "+l[1]+"\n"if l[1]!=""else"")+("Emplacement: "+l[2]+"\n"if l[2]!=""else"")+("Caractéristique: "+l[3]if l[3]!=""else""))
    else:
        contextual_bot.reply(ContextualBot.TEXT, "Trop de résultats")



def deprecatedCommand(contextual_bot, sh_core):
    contextual_bot.reply(ContextualBot.TEXT, "Cette commande n'est plus supportée")
    contextual_bot.outputMessages()
    contextual_bot.reply(ContextualBot.VIDEO, dataServerAddress+'tintin_c\'est_con_capitaine.mp4')
    contextual_bot.outputMessages()
    contextual_bot.reply(ContextualBot.TEXT, "Consultez l'aide (/help) pour découvrir les commandes alternatives")
    contextual_bot.outputMessages()

#########################################################################################
#                                     CITATIONS                                         #
#########################################################################################

def getRandomLine(txt):
    l = txt.split('\n')
    return l[random.randint(0, len(l)-2)]
def getCitation(contextual_bot, sh_core):
    contextual_bot.reply(ContextualBot.TEXT, getRandomLine(open(mapPath+"citations", "r").read()))
def getCitations(contextual_bot, sh_core):
    FLM_getFile(contextual_bot, sh_core, "citations")
def addCitation(contextual_bot, sh_core):
    FLM_addLine(contextual_bot, sh_core, "citations")

def get1AProject(contextual_bot, sh_core):
    FLM_getFile(contextual_bot, sh_core, "projets1A")
def add1AProject(contextual_bot, sh_core):
    FLM_addLine(contextual_bot, sh_core, "projets1A")

def addNewVideo(contextual_bot, sh_core):
    FLM_addLine(contextual_bot, sh_core, "new_videos")

def addCard(contextual_bot, sh_core):
    FLM_addLine(contextual_bot, sh_core, "cards")
def showCards(contextual_bot, sh_core):
    FLM_getFile(contextual_bot, sh_core, "cards")

def add2060(contextual_bot, sh_core):
    FLM_addLine(contextual_bot, sh_core, "questions_for_2060")
def show2060(contextual_bot, sh_core):
    FLM_getFile(contextual_bot, sh_core, "questions_for_2060")

#########################################################################################
#                                       Forward                                         #
#########################################################################################

def generic_handle_text(contextual_bot, sh_core):
    msg = contextual_bot.getText()
    if len(msg)==0:return
    if msg[0] == '/':
        for (fun_txt, fun) in commands:
            if msg[1:].startswith(fun_txt) and (len(msg[1:])==len(fun_txt) or msg[len(fun_txt)+1]==' '):
                fun(contextual_bot, sh_core)
    else:
        highLevelTextCallback(contextual_bot, sh_core)

#########################################################################################
#                                       MUSIC                                           #
#########################################################################################

musicQueue = MusicQueue()
def addMusic(contextual_bot, sh_core):#/addm
    data = contextual_bot.getText().split(' ')
    contextual_bot.reply(ContextualBot.TEXT, "Adding data...")
    contextual_bot.outputMessages()
    (updated, size) = musicQueue.add(data[1])
    if not updated:
        contextual_bot.reply(ContextualBot.TEXT, str(size)+"  videos added from local cache\nType /fetch to update cache")
    else:
        contextual_bot.reply(ContextualBot.TEXT, str(size)+"  video(s) added")
    contextual_bot.reply(ContextualBot.TEXT, str(len(musicQueue.queue))+"  video(s) in total")
    if "shuffle" in data:
        musicQueue.shuffle()
def shuffleMusic(contextual_bot, sh_core):#/shuffle
    musicQueue.shuffle()
    contextual_bot.reply(ContextualBot.TEXT, "Done")
def clearMusic(contextual_bot, sh_core):#/clear
    musicQueue.clear()
    contextual_bot.reply(ContextualBot.TEXT, "Done")
def updateMusic(contextual_bot, sh_core):#/fetch
    if musicQueue.playlist == None:
        contextual_bot.reply(ContextualBot.TEXT, "No playlist to update")
    else:
        contextual_bot.reply(ContextualBot.TEXT, "Updating playlist cache...")
        contextual_bot.outputMessages()
        old_size = musicQueue.playlist.size
        musicQueue.updatePlaylist()
        contextual_bot.reply(ContextualBot.TEXT, "Playlist updated ("+str(musicQueue.playlist.size-old_size)+" new videos)")
def infoMusic(contextual_bot, sh_core):#/queue
    contextual_bot.reply(ContextualBot.TEXT, str(len(musicQueue.queue))+"  video(s)\nCursor: "+str(musicQueue.cursor))
def setCursorMusic(contextual_bot, sh_core):
    musicQueue.setCursor(int(contextual_bot.getText().split(' ')[1]))

#########################################################################################
#                                       DISCORD                                         #
#########################################################################################

#https://discord.com/api/oauth2/authorize?client_id=693578928777854986&permissions=3197504&scope=bot
music_increment = 1
async def discordPlay(message):
    if len(musicQueue.queue) == 0:return
    musicQueue.playNext(tempPath+'v.mp3')
    await discordPlayFile(message, tempPath+'v.mp3', discordPlayNext)
def discordPlayNext(err):
    global discord_voice
    global music_increment
    if music_increment == 0:
        music_increment = 1
        return
    elif music_increment == 1:
        musicQueue.playNext(tempPath+'v.mp3')
    elif music_increment == -1:
        musicQueue.playPrevious(tempPath+'v.mp3')
        music_increment = 1
    source = FFmpegPCMAudio(executable=ffmpeg_path, source=tempPath+'v.mp3')
    discord_voice.play(source, after=discordPlayNext)
async def discordPause(message):
    global discord_voice
    discord_voice.pause()
async def discordResume(message):
    global discord_voice
    discord_voice.resume()
async def discordStop(message):
    global music_increment
    global discord_voice
    music_increment = 0
    discord_voice.stop()
async def discordNext(message):
    global discord_voice
    discord_voice.stop()
async def discordPrevious(message):
    global discord_voice
    global music_increment
    music_increment = -1
    discord_voice.stop()
async def discordInfo(message):
    await message.channel.send(musicQueue.getCurrentURL())

async def discordPlayMic(message):
    global discord_voice
    channel = message.author.voice.channel
    if not channel:
        print("You are not connected to a voice channel")
        return
    discord_voice = get(client_discord.voice_clients, guild=message.guild)
    if discord_voice and discord_voice.is_connected():
        await discord_voice.move_to(channel)
    else:
        discord_voice = await channel.connect()
    source = discord.FFmpegAudio(source="audio=\"Réseau de microphones (Realtek High Definition Audio)\"", executable=ffmpeg_path, before_options="-f dshow")
    discord_voice.play(source)

#ffmpeg -f dshow -i audio="Réseau de microphones (Realtek High Definition Audio)" -acodec libmp3lame  -t 10 out.mp3

async def discordSay(message):
    getVoice(message.content[6:], tempPath+'v.mp3')
    await discordPlayFile(message, tempPath+'v.mp3')
def default_discord_end(err):
    a = 42*10
async def discordPlayFile(message, file, after_playing=default_discord_end):
    global discord_voice
    channel = message.author.voice.channel
    if not channel:
        print("You are not connected to a voice channel")
        return
    discord_voice = get(client_discord.voice_clients, guild=message.guild)
    if discord_voice and discord_voice.is_connected():
        await discord_voice.move_to(channel)
    else:
        discord_voice = await channel.connect()
    source = FFmpegPCMAudio(executable=ffmpeg_path, source=file)
    discord_voice.play(source, after=after_playing)
async def discordDisconnect():
    global discord_voice
    await discord_voice.disconnect()


#########################################################################################
#                                      TELEGRAM                                         #
#########################################################################################

# Target chat
def telegram_conv(update, context):
    conv(TelegramBot(update, context))
# Forward incoming text from Telegram to global core
def telegram_handle_command(update, context):
    contextual_bot = TelegramBot(update, context)
    generic_handle_text(contextual_bot, sh_core)
    contextual_bot.outputMessages()

def telegram_handle_video(update, context):
    handle_video(update, context, sh_core)

# Shutdown all system
def shutdown():
    eventsUI.stop() # Stop event thread
    brendapi.stop() # Kill BrendAPI
    sh_core.remote_service.stop() # Kill remote service
    stop_periodic_thread_fun() # Kill Mail and Twitter
    updater.stop() # Kill Telegram
    updater.is_idle = False
    os.kill(os.getpid(), signal.SIGINT) # Kill Discord
def stopAll():
    threading.Thread(target=shutdown).start()
# Shutdown command from Telegram
def telegram_stop(update, context):
    if update.message.from_user.id == super_admin:
        context.bot.send_message(update.message.chat_id, "Stopping...")
        stopAll()

def voice_handler(update, context):
    update.message.voice.get_file().download(tempPath+"out.ogg")
    contextual_bot = SpeechBot2(update, context, speechToText(tempPath+"out.ogg"))
    generic_handle_text(contextual_bot, sh_core)
    contextual_bot.outputMessages()


def telegram_new_member(update, context):
    dm = data_manager.DataManager()
    contextual_bot = TelegramBot(update, context)
    members = update.message.new_chat_members
    ptdrtki = False
    for m in members:
        print(str(m))
        if m.id == id_bot:
            # Bot has been added to the chat
            contextual_bot.reply(ContextualBot.VIDEO, dataServerAddress+'eddy_malou_bonjour.mp4')
            contextual_bot.outputMessages()
            contextual_bot.reply(ContextualBot.TEXT, "Aide: /help\nConfiguration: /on, /off, /config, /proba")
            contextual_bot.outputMessages()
            # Init default welcome message in chat group with historic "PTDR T KI"
            dm.saveRessource(contextual_bot.getChatID(), "welcome", 'SCAACAgQAAxkBAAIPVmUm4YE6sR4VTIZvRAmjB_topb1KAAJbBwACTcfgUrO3oPsTnHZbMAQ')
        else:
            ptdrtki = True
        if m.id == conv_perso:
            ptdrtki = False
            pack = sh_core.telegramBot.get_sticker_set("EIRBOTO")
            contextual_bot.reply(ContextualBot.STICKER, pack.stickers[12])
            contextual_bot.outputMessages()
    if ptdrtki:
        message = dm.getRessource(contextual_bot.getChatID(), "welcome")
        if len(message) > 2:
            if message[0] == 'T':
                contextual_bot.reply(ContextualBot.TEXT, message[1:])
                contextual_bot.outputMessages()
            elif message[0] == 'S':
                contextual_bot.reply(ContextualBot.STICKER, message[1:])
                contextual_bot.outputMessages()
            elif message[0] == 'V':
                contextual_bot.reply(ContextualBot.VIDEO, message[1:])
                contextual_bot.outputMessages()

def telegram_delete(update, context):
    try:
        context.bot.deleteMessage(update.message.chat_id, update.message.reply_to_message.message_id)
        context.bot.deleteMessage(update.message.chat_id, update.message.message_id)
    except Exception as e:
        print("E") #EEEEEEEEEEEEEEEEEEEEEEE


#########################################################################################
#                                     BRENDAPI                                          #
#########################################################################################

# Callback on received packets from BrendAPI
def brendapiCallbackOnText(text, brendapi, clientsocket, addr):
    contextual_bot = BrendapiBot(text, brendapi, clientsocket, addr)
    # Allow monitoring only if requests are local
    (ip_a, _) = addr
    # if ip_a == "127.0.1.1":
    #     if text[:8] == "/monitor": # Monitor commands
    #         commands = text.split(' ')
    #         if commands[1] == "stop": # Stop system
    #             contextual_bot.reply(ContextualBot.TEXT, "STOP")
    #             contextual_bot.outputMessages()
    #             stopAll()
    # else:
    # Call global core
    generic_handle_text(contextual_bot, sh_core)
    contextual_bot.outputMessages()


#########################################################################################
#                                        MAIL                                           #
#########################################################################################

def initMailBot():
    global mail_manager
    mail_manager = MailManager("brenda.tobrie@gmail.com", tokens[26])
def runMailBot():
    mails = mail_manager.getAllMails()
    # Call global core with each new mail
    for m in mails:
        #print(m)
        contextual_bot = MailBot(mail_manager, m)
        generic_handle_text(contextual_bot, sh_core)
        contextual_bot.outputMessages()
def forceMailUpdate(update, context):
    context.bot.send_message(update.message.chat_id, "Updating mails...")
    runMailBot()

#########################################################################################
#                                      TWITTER                                          #
#########################################################################################

def initTweepy():
    global tweepy_since_id
    global tweepy_api
    tweepy_since_id = 999999999
    tweepy_auth = tweepy.OAuthHandler(tokens[20], tokens[21])
    tweepy_auth.set_access_token(tokens[22], tokens[23])
    tweepy_api = tweepy.API(tweepy_auth)
def check_mentions(tweepy_api, since_id, output):
    new_since_id = since_id
    for tweet in tweepy.Cursor(tweepy_api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if output:
            if tweet.in_reply_to_status_id is not None:
                continue
            contextual_bot = TweepyBot(tweepy_api, tweet)
            generic_handle_text(contextual_bot, sh_core)
            contextual_bot.outputMessages()
    return new_since_id
def startTweepy():
    global tweepy_since_id
    tweepy_since_id = check_mentions(tweepy_api, 1, False)
def runTweepy():
    global tweepy_since_id
    tweepy_since_id = check_mentions(tweepy_api, tweepy_since_id, True)


#########################################################################################
#                                  PERIODIC THREAD                                      #
#########################################################################################

def periodic_thread_wait(t):
    global stop_periodic_thread
    global periodic_thread_watchdog
    for i in range(t//5):
        time.sleep(5)
        if stop_periodic_thread:
            return True
        periodic_thread_watchdog = (periodic_thread_watchdog+1)%256
    return False
def periodic_thread():
    while True:
        runMailBot()
        #runTweepy()
        if periodic_thread_wait(10 if TEST else 300):
            break
global stop_periodic_thread
stop_periodic_thread = True
def start_periodic_thread():
    global stop_periodic_thread
    global periodic_thread_watchdog
    stop_periodic_thread = False
    periodic_thread_watchdog = 0
    threading.Thread(target=periodic_thread).start()
def stop_periodic_thread_fun():
    global stop_periodic_thread
    if not stop_periodic_thread:
        stop_periodic_thread = True
        time.sleep(5)
def telegram_periodic_thread(update, context):
    if update.message.from_user.id == super_admin:
        arg=update.message.text[5:]
        if arg == "a":
            context.bot.send_message(update.message.chat_id, "Starting periodic thread")
            start_periodic_thread()
        if arg == "o":
            context.bot.send_message(update.message.chat_id, "Stoping periodic thread")
            stop_periodic_thread_fun()
        if arg == "c":
            context.bot.send_message(update.message.chat_id, "Watchdog: "+str(periodic_thread_watchdog))

#########################################################################################
#                                       EVENTS                                          #
#########################################################################################

global eventsUI
eventsUI = events_ui.EventsUI()


#########################################################################################
#                                        MAIN                                           #
#########################################################################################

# APIs enable
TELEGRAM_ENABLE = True or not(TEST)
DISCORD_ENABLE  = False or not(TEST)
PERIODIC_ENABLE = False# or not(TEST)
BRENDAPI_ENABLE = True or not(TEST)
EVENTS_ENABLE = True or not(TEST)

# Retrieve tokens from file
tokens = open("tokens", "r").read().split("\n")
TELEGRAM_TOKEN=tokens[2] if TEST else tokens[0]
DISCORD_TOKEN = tokens[16]
OPENAI_TOKEN = tokens[27]

openai.api_key = OPENAI_TOKEN

# Some init with global variables
updater = Updater(TELEGRAM_TOKEN, use_context=True)
sh_core = SharedCore(updater.bot, RemoteServiceServer(65332))
client_discord = discord.Client()


# To add a new command, add a line in this list.
# A command is described with a tuple containing
#    - a string that triggers the command if detected in a text chat
#    - a function called when the command string is matched
# Those commands are generic for all APIs (Telegram, Discord, etc...)
# If adding a command here, you should consider
# adding a help description in the help.txt file.
commands = [
("di", deprecatedCommand), ("video", deprecatedCommand),
("config", configureParameters),("proba", configureProba),
("on", setAutoReplyOn),("off", setAutoReplyOff),("find", find),("info", info),
("quote", quote),
("meme", meme),("calc", calc), ("croa", croa),
("addc", addCitation),("citations", getCitations),("citation", getCitation),
("addp", add1AProject),("sprojet", get1AProject),
("addcard", addCard),("scards", showCards),
("add2060", add2060),("s2060", show2060),
("say2", sayText), ("say", sayText2), ("lang", setVoiceLanguage), ("speed", setVoiceSpeed),
("img", search_image), ("sound", search_sound), ("morse", morse),
("addm", addMusic),
("shuffle", shuffleMusic),("clear", clearMusic),("fetch", updateMusic),("queue", infoMusic),
("cursor", setCursorMusic),
("help", help),
("addv", addNewVideo),
("event", eventsUI.addEvent),
("mainevent", eventsUI.setMainEvent),
("countdown", eventsUI.reactMainEvent),
("genre", outputGenre),
("playlists", outputPlaylists),
("horaires", outputHoraires),
("gptstart", GPT_startConvMode),
("gptstop", GPT_stopConvMode),
("gptconfig", GPT_setSystemPrompt),
("porte", porteMegane),
("welcome", setWelcomeMessage),
("bureau", bureauList),
("pdf", pdfConvert),
("card", creditCard)
]


def main():

    #####[ BRENDAPI ]#####
    global brendapi
    brendapi = Brendapi(53720, brendapiCallbackOnText)
    if BRENDAPI_ENABLE:
        brendapi.start()

    #####[ REMOTE SERVICE ]#####
    if not TEST:
        sh_core.remote_service.start()

    #####[ MAIL & TWITTER ]#####
    initMailBot()
    initTweepy()
    if PERIODIC_ENABLE:
        print("Start periodic")
        start_periodic_thread()
        print("Periodic ok")

    #####[ EVENTS ]#####
    if EVENTS_ENABLE:
        eventsUI.init(sh_core)

    #####[ TELEGRAM ]#####
    dp = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    if TELEGRAM_ENABLE:
        dp.add_handler(InlineQueryHandler(inlinequery))

        for (fun_txt, fun) in commands:
            dp.add_handler(CommandHandler(fun_txt, telegram_handle_command))

        dp.add_handler(CommandHandler('list',list))
        dp.add_handler(CommandHandler('dico',dico))
        dp.add_handler(CommandHandler('rapport',rapport))
        dp.add_handler(CommandHandler('update',update_video_names_command))

        #Personal commands
        dp.add_handler(CommandHandler('conv', telegram_conv))
        dp.add_handler(CommandHandler('stopall', telegram_stop))
        dp.add_handler(CommandHandler('mail', forceMailUpdate))
        dp.add_handler(CommandHandler('per', telegram_periodic_thread))
        dp.add_handler(CommandHandler('del', telegram_delete))

        dp.add_handler(MessageHandler(Filters.text, telegram_handle_command))

        dp.add_handler(MessageHandler(Filters.voice, voice_handler))

        dp.add_handler(MessageHandler(Filters.video, telegram_handle_video))

        dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, telegram_new_member))

        updater.start_polling()
        if not DISCORD_ENABLE:
            updater.idle()

    #####[ DISCORD ]#####
    if DISCORD_ENABLE:
        @client_discord.event
        async def on_message(message):
            if message.author == client_discord.user:
                return
            contextual_bot = DiscordBot(message)
            if message.content.startswith("/dsay"):
                await discordSay(message)
            if message.content.startswith("/play"):
                await discordPlay(message)
            if message.content.startswith("/pause"):
                await discordPause(message)
            if message.content.startswith("/resume"):
                await discordResume(message)
            if message.content.startswith("/next"):
                await discordNext(message)
            if message.content.startswith("/previous"):
                await discordPrevious(message)
            if message.content.startswith("/stop"):
                await discordStop(message)
            if message.content.startswith("/pn"):
                await discordInfo(message)
            if message.content.startswith("/mic"):
                await discordPlayMic(message)
            if message.content.startswith("/quit"):
                await discordDisconnect()
            generic_handle_text(contextual_bot, sh_core)
            await contextual_bot.outputMessages()
        @client_discord.event
        async def on_ready():
            print('Connected to Discord!')
        client_discord.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
