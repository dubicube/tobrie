#sudo apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev
#pip install python-telegram-bot==12.0.0b1 --upgrade


import discord

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

from config import *
from contextual_bot import *
from shared_core import *
from web_texts import *
from inventory import *
from audio import *
from auto_reply import handleText, load_maps, setDI, setAutoReply, conv

sticker_map_regex = []
text_map_regex = []
video_map_regex = []

sh_core = None

########################################################################################################################################################
#                                                                  VIDEO QUERY                                                                         #
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

########################################################################################################################################################
#                                                              AUDIO                                                                                   #
########################################################################################################################################################

def calc(update, context):
    sh_core.notifConsole(TelegramBot(update, context))
    context.bot.send_chat_action(update.message.chat_id, 'upload_audio')
    calculate(update.message.text[6:], soundPath)
    context.bot.send_audio(chat_id=update.message.chat_id, audio=open(soundPath+"v.mp3", 'rb'))

def croa(update, context):
    sh_core.notifConsole(TelegramBot(update, context))
    context.bot.send_chat_action(update.message.chat_id, 'upload_audio')
    v = 1
    if len(update.message.text[6:]) > 0 and int(update.message.text[6:]) < 100:
        v = int(update.message.text[6:])
    duplicateAudio(soundPath+"croa"+".wav", soundPath+"v.wav", v)
    context.bot.send_audio(chat_id=update.message.chat_id, audio=open(soundPath+"v.mp3", 'rb'))


########################################################################################################################################################
#                                                              OTHER COMMANDS                                                                          #
########################################################################################################################################################

def meme(update, context):
    sh_core.notifConsole(TelegramBot(update, context))
    memes = [f for f in os.listdir(memePath) if os.path.isfile(os.path.join(memePath, f))]
    m = memes[random.randint(0, len(memes)-1)]
    context.bot.send_photo(update.message.chat_id, open(memePath+m, 'rb'))

def help(update, context):
    sh_core.notifConsole(TelegramBot(update, context))
    context.bot.send_message(chat_id=update.message.chat_id, text=open("help.txt", "r").read())


########################################################################################################################################################
#                                                                TEXTS FROM WEB                                                                        #
########################################################################################################################################################

def info(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    contextual_bot.replyText(getInfo())
def quote(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    contextual_bot.replyText(getQuote())

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
#                                                                       INVENTORY                                                                      #
########################################################################################################################################################

inventory = []
if not(TEST):
    inventory = processInventoryHTML("base.html")
def find(contextual_bot):
    results = searchInventory(contextual_bot.getText()[6:], inventory)
    if len(results) < 10:
        for l in results:
            contextual_bot.replyText((("Référence: "+l[0]+"\n")if l[0]!=""else"")+("Nom: "+l[1]+"\n"if l[1]!=""else"")+("Emplacement: "+l[2]+"\n"if l[2]!=""else"")+("Caractéristique: "+l[3]if l[3]!=""else""))
    else:
        contextual_bot.replyText("Trop de résultats")


########################################################################################################################################################
#                                                        Telegram generic forward                                                                      #
########################################################################################################################################################

def telegram_handleText(update, context):
    handleText(TelegramBot(update, context), sh_core)
def telegram_setDI(update, context):
    setDI(TelegramBot(update, context), sh_core)
def telegram_setAutoReply(update, context):
    setAutoReply(TelegramBot(update, context), sh_core)
def telegram_conv(update, context):
    conv(TelegramBot(update, context))
def telegram_find(update, context):
    find(TelegramBot(update, context))
def telegram_info(update, context):
    info(TelegramBot(update, context), sh_core)
def telegram_quote(update, context):
    quote(TelegramBot(update, context), sh_core)

########################################################################################################################################################
#                                                                       MAIN                                                                           #
########################################################################################################################################################

tokens = open("tokens", "r").read().split("\n")
TELEGRAM_TOKEN=tokens[2] if TEST else tokens[0]
DISCORD_TOKEN = tokens[16]
updater = Updater(TELEGRAM_TOKEN, use_context=True)
sh_core = SharedCore(updater.bot)

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
    dp.add_handler(MessageHandler(Filters.text, telegram_handleText))
    dp.add_handler(InlineQueryHandler(inlinequery))
    #dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(CommandHandler('list',list))
    dp.add_handler(CommandHandler('dico',dico))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(CommandHandler('calc',calc))
    dp.add_handler(CommandHandler('meme',meme))

    dp.add_handler(CommandHandler('info', telegram_info))
    dp.add_handler(CommandHandler('quote', telegram_quote))
    dp.add_handler(CommandHandler('di', telegram_setDI))
    dp.add_handler(CommandHandler('video', telegram_setAutoReply))
    dp.add_handler(CommandHandler('find',telegram_find))

    dp.add_handler(CommandHandler('rapport',rapport))
    dp.add_handler(CommandHandler('update',update_video_names_command))

    dp.add_handler(CommandHandler('croa',croa))

    #Personal commands
    dp.add_handler(CommandHandler('conv', telegram_conv))
    dp.add_handler(CommandHandler('stop', stop))

    updater.start_polling()
    #updater.idle()


    #####  DISCORD  #####
    client = discord.Client()
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        contextual_bot = DiscordBot(message)
        if message.content[0] == '/':
            if message.content[1:] == "di":
                setDI(contextual_bot, sh_core)
            if message.content[1:] == "video":
                setAutoReply(contextual_bot, sh_core)
            if message.content[1:5] == "find":
                find(contextual_bot)
            if message.content[1:] == "info":
                info(contextual_bot, sh_core)
            if message.content[1:] == "quote":
                quote(contextual_bot, sh_core)
        else:
            handleText(contextual_bot, sh_core)
        await contextual_bot.outputMessages()
    @client.event
    async def on_ready():
        print('Connected to Discord!')
    client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
