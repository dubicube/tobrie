import discord
from discord import FFmpegPCMAudio
from discord.utils import get

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
from urllib import request

import threading

from config import *
from contextual_bot import *
from shared_core import *
from web_texts import *
from inventory import *
from audio import *
from auto_reply import handleText, load_maps, setDI, setAutoReply, conv
from youtube import *
from mail_manager import *

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
voiceLanguage = "fr-FR"
def sayText(contextual_bot, sh_core):
    getVoice(contextual_bot.getText()[5:], soundPath+'v.mp3', voiceLanguage)
    contextual_bot.reply(ContextualBot.AUDIO, open(soundPath+'v.mp3', 'rb'))

def setVoiceLanguage(contextual_bot, sh_core):
    global voiceLanguage
    t = contextual_bot.getText()[6:]
    h = [i[1:].split("\">") for i in getHelp("lang").split('\n')[5:-1]]
    value = [i[0] for i in h]
    text = [i[1] for i in h]
    if t in value:
        i = value.index(t)
        voiceLanguage = t
        contextual_bot.reply(ContextualBot.TEXT, "Language selected:\n"+text[i])
    else:
        contextual_bot.reply(ContextualBot.TEXT, "Language not found\nType \"/help lang\" for more information")

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
        image_name = "temp/out."+extension
        download_image(url, image_name)
        contextual_bot.reply(ContextualBot.IMAGE, open(image_name, "rb"))

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
def get1AProject(contextual_bot, sh_core):
    contextual_bot.reply(ContextualBot.TEXT, open("maps/projets1A", "r").read())
def add1AProject(contextual_bot, sh_core):
    txt = contextual_bot.getText()[6:].split('\n')[0]
    if len(txt) > 1:
        f = open("maps/projets1A", "a")
        f.write(txt+"\n")
        f.close()
        contextual_bot.reply(ContextualBot.TEXT, "Ok")
    else:
        contextual_bot.reply(ContextualBot.TEXT, "Nop")

#########################################################################################
#                                       MUSIC                                           #
#########################################################################################

musicQueue = MusicQueue()
def addMusic(contextual_bot, sh_core):#/addm
    data = contextual_bot.getText()
    i = data.find(' ')
    contextual_bot.reply(ContextualBot.TEXT, "Adding data...")
    contextual_bot.outputMessages()
    (updated, size) = musicQueue.add(data[i+1:])
    if not updated:
        contextual_bot.reply(ContextualBot.TEXT, str(size)+"  videos loaded from local cache\nType /fetch to update cache")
    else:
        contextual_bot.reply(ContextualBot.TEXT, str(size)+"  video(s) loaded")
    contextual_bot.reply(ContextualBot.TEXT, str(len(musicQueue.queue))+"  video(s) in total")
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
    contextual_bot.reply(ContextualBot.TEXT, str(len(musicQueue.queue))+"  video(s)")

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
        handleText(contextual_bot, sh_core)

#########################################################################################
#                                       DISCORD                                         #
#########################################################################################

#https://discord.com/api/oauth2/authorize?client_id=693578928777854986&permissions=3197504&scope=bot

async def discordPlay(message):
    if len(musicQueue.queue) == 0:return
    musicQueue.queue[0].download('temp/v.mp3')
    musicQueue.queue = musicQueue.queue[1:]
    await discordPlayFile(message, 'temp/v.mp3', discordPlayNext)
def discordPlayNext(err):
    global discord_voice
    musicQueue.queue[0].download('temp/v.mp3')
    musicQueue.queue = musicQueue.queue[1:]
    source = FFmpegPCMAudio(executable=ffmpeg_path, source='temp/v.mp3')
    discord_voice.play(source, after=discordPlayNext)

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
    getVoice(message.content[6:], 'temp/v.mp3')
    await discordPlayFile(message, 'temp/v.mp3')
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

def telegram_conv(update, context):
    conv(TelegramBot(update, context))

def telegram_handle_command(update, context):
    contextual_bot = TelegramBot(update, context)
    generic_handle_text(contextual_bot, sh_core)
    contextual_bot.outputMessages()

# Shutdown Telegram bot
def shutdown():
    updater.stop()
    updater.is_idle = False
def stop(update, context):
    if update.message.from_user.id == super_admin:
        context.bot.send_message(update.message.chat_id, "Stopping...")
        global stop_periodic_thread
        stop_periodic_thread = True
        threading.Thread(target=shutdown).start()


#########################################################################################
#                                        MAIL                                           #
#########################################################################################

def initMailBot():
    global mail_manager
    mail_manager = MailManager("brenda.tobrie@gmail.com", tokens[26])
def runMailBot():
    mails = mail_manager.getAllMails()
    for m in mails:
        print(m)
        contextual_bot = MailBot(mail_manager, m)
        generic_handle_text(contextual_bot, sh_core)
        contextual_bot.outputMessages()
def forceMailUpdate(update, context):
    if update.message.from_user.id == super_admin:
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
            break
        periodic_thread_watchdog = (periodic_thread_watchdog+1)%256
def periodic_thread():
    while True:
        runMailBot()
        #runTweepy()
        periodic_thread_wait(10 if TEST else 300)
def start_periodic_thread():
    global stop_periodic_thread
    global periodic_thread_watchdog
    stop_periodic_thread = False
    periodic_thread_watchdog = 0
    threading.Thread(target=periodic_thread).start()
def stop_periodic_thread():
    global stop_periodic_thread
    stop_periodic_thread = True
def telegram_periodic_thread(update, context):
    if update.message.from_user.id == super_admin:
        arg=update.message.text[5:]
        if arg == "a":
            context.bot.send_message(update.message.chat_id, "Starting periodic thread")
            start_periodic_thread()
        if arg == "o":
            context.bot.send_message(update.message.chat_id, "Stoping periodic thread")
            stop_periodic_thread()
        if arg == "c":
            context.bot.send_message(update.message.chat_id, "Watchdog: "+str(periodic_thread_watchdog))


#########################################################################################
#                                        MAIN                                           #
#########################################################################################


TELEGRAM_ENABLE = True or not(TEST)
DISCORD_ENABLE  = False or not(TEST)
PERIODIC_ENABLE = False

tokens = open("tokens", "r").read().split("\n")
TELEGRAM_TOKEN=tokens[2] if TEST else tokens[0]
DISCORD_TOKEN = tokens[16]
updater = Updater(TELEGRAM_TOKEN, use_context=True)
sh_core = SharedCore(updater.bot)
client_discord = discord.Client()

commands = [
("di", setDI),("video", setAutoReply),("find", find),("info", info),
("quote", quote),("citation", getCitation), ("addc", addCitation), ("projet", get1AProject),
("addp", add1AProject),("meme", meme),("calc", calc), ("croa", croa),
("say", sayText), ("lang", setVoiceLanguage),("img", search_image),("addm", addMusic),
("shuffle", shuffleMusic),("clear", clearMusic),("fetch", updateMusic),("queue", infoMusic),
("help", help)
]

def main():

    #####[ MAIL & TWITTER ]#####
    initMailBot()
    initTweepy()
    if PERIODIC_ENABLE:
        start_periodic_thread()

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
        dp.add_handler(CommandHandler('stopall', stop))
        dp.add_handler(CommandHandler('mail', forceMailUpdate))
        dp.add_handler(CommandHandler('per', telegram_periodic_thread))

        dp.add_handler(MessageHandler(Filters.text, telegram_handle_command))

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
            if contextual_bot.isChatPerso():
                if message.content == "/stopall":
                    await client_discord.close()
            if message.content.startswith("/dsay"):
                await discordSay(message)
            if message.content.startswith("/play"):
                await discordPlay(message)
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
