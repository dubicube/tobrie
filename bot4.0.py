import discord

import tweepy

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
import requests
from zalgo_text import zalgo
import urllib.parse
import urllib.request

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
    contextual_bot.reply(ContextualBot.AUDIO, open(soundPath+"v.mp3", 'rb'))


#########################################################################################
#                                   OTHER COMMANDS                                      #
#########################################################################################

def meme(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    memes = [f for f in os.listdir(memePath) if os.path.isfile(os.path.join(memePath, f))]
    m = memes[random.randint(0, len(memes)-1)]
    contextual_bot.reply(ContextualBot.IMAGE, open(memePath+m, 'rb'))

def help(update, context):
    sh_core.notifConsole(TelegramBot(update, context))
    context.bot.send_message(chat_id=update.message.chat_id, text=open("help.txt", "r").read())


#########################################################################################
#                                   USELESS TEXTS                                       #
#########################################################################################

def info(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    contextual_bot.reply(ContextualBot.TEXT, getInfo())
def quote(contextual_bot, sh_core):
    sh_core.notifConsole(contextual_bot)
    contextual_bot.reply(ContextualBot.TEXT, getQuote())

#########################################################################################
#                                       RAPPORT                                         #
#########################################################################################

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

#########################################################################################
#                                      INVENTORY                                        #
#########################################################################################

inventory = []
if not(TEST):
    inventory = processInventoryHTML("base.html")
def find(contextual_bot, sh_core):
    results = searchInventory(contextual_bot.getText()[6:], inventory)
    if len(results) < 10:
        for l in results:
            contextual_bot.reply(ContextualBot.TEXT, (("Référence: "+l[0]+"\n")if l[0]!=""else"")+("Nom: "+l[1]+"\n"if l[1]!=""else"")+("Emplacement: "+l[2]+"\n"if l[2]!=""else"")+("Caractéristique: "+l[3]if l[3]!=""else""))
    else:
        contextual_bot.reply(ContextualBot.TEXT, "Trop de résultats")

#########################################################################################
#                                     CITATIONS                                         #
#########################################################################################

def getRandomLine(txt):
    l = txt.split('\n')
    return l[random.randint(0, len(l)-2)]
def getCitation(contextual_bot, sh_core):
    contextual_bot.reply(ContextualBot.TEXT, getRandomLine(open("maps/citations", "r").read()))
def addCitation(contextual_bot, sh_core):
    txt = contextual_bot.getText()[6:].split('\n')[0]
    if len(txt) > 1:
        f = open("maps/citations", "a")
        f.write(txt+"\n")
        f.close()
        contextual_bot.reply(ContextualBot.TEXT, "Ok")
    else:
        contextual_bot.reply(ContextualBot.TEXT, "Nop")

#########################################################################################
#                                       Forward                                         #
#########################################################################################

def telegram_conv(update, context):
    conv(TelegramBot(update, context))

def telegram_handle_command(update, context):
    contextual_bot = TelegramBot(update, context)
    generic_handle_text(contextual_bot, sh_core)
    contextual_bot.outputMessages()

def generic_handle_text(contextual_bot, sh_core):
    msg = contextual_bot.getText()
    if msg[0] == '/':
        for (fun_txt, fun) in commands:
            if msg[1:].startswith(fun_txt):
                fun(contextual_bot, sh_core)
    else:
        handleText(contextual_bot, sh_core)

#########################################################################################
#                                        MAIN                                           #
#########################################################################################


commands = [("di", setDI), ("video", setAutoReply), ("find", find), ("info", info), ("quote", quote),
("citation", getCitation), ("addr", addCitation), ("meme", meme), ("calc", calc), ("croa", croa)]


tokens = open("tokens", "r").read().split("\n")
TELEGRAM_TOKEN=tokens[2] if TEST else tokens[0]
DISCORD_TOKEN = tokens[16]
updater = Updater(TELEGRAM_TOKEN, use_context=True)
sh_core = SharedCore(updater.bot)

# Shutdown Telegram bot
def shutdown():
    updater.stop()
    updater.is_idle = False
def stop(update, context):
    if update.message.from_user.id == super_admin:
        context.bot.send_message(update.message.chat_id, "Stopping...")
        threading.Thread(target=shutdown).start()


client_discord = discord.Client()


#####  TWITTER  #####

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
def tweepy_thread():
    since_id = check_mentions(tweepy_api, 1, False)
    while True:
        since_id = check_mentions(tweepy_api, since_id, True)
        time.sleep(30)
if not TEST:
    threading.Thread(target=tweepy_thread).start()

def main():

    #####  TELEGRAM  #####
    dp = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    dp.add_handler(MessageHandler(Filters.text, telegram_handle_command))
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_handler(CommandHandler('list',list))
    dp.add_handler(CommandHandler('dico',dico))
    dp.add_handler(CommandHandler('help',help))

    for (fun_txt, fun) in commands:
        dp.add_handler(CommandHandler(fun_txt, telegram_handle_command))

    dp.add_handler(CommandHandler('rapport',rapport))
    dp.add_handler(CommandHandler('update',update_video_names_command))

    #Personal commands
    dp.add_handler(CommandHandler('conv', telegram_conv))
    dp.add_handler(CommandHandler('stop', stop))

    updater.start_polling()

    if TEST:
        updater.idle()
    else:
        #threading.Thread(target=shutdown).start()
        #####  DISCORD  #####
        @client_discord.event
        async def on_message(message):
            if message.author == client_discord.user:
                return
            contextual_bot = DiscordBot(message)
            if message.content == "/stop":
                await client_discord.close()
            else:
                generic_handle_text(contextual_bot, sh_core)
            await contextual_bot.outputMessages()
        @client_discord.event
        async def on_ready():
            print('Connected to Discord!')
        client_discord.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
