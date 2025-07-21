import asyncio as asyncioDeepShit
from datetime import datetime, timedelta
import events
import data_manager
from contextual_bot import *
from random import randint

from zalgo_text import zalgo

from generic.web_texts import *
from auto_reply import getRandomVideoURL

from generic.dateFuns import *

def getRandomDateTime(proba):
    # proba=100 => every 3 seconds
    # proba=90 => once in 1 mn
    # proba=75 => once in 2 hrs 16mn
    # proba=50=> once in 1 day 16 hrs
    # proba=10 => once in 9 days 12 hrs
    # proba=1 => once in 30 days (but not exactly, it is a random date in the month, so it will happen more than once a month)

    pFactor = 100000 # Magic number, to get an exponential scale of the probability vs delay
    maxSeconds = int(3 + (  (pFactor**(1.0-proba/100.0) - 1) / pFactor  )*(30*24*3600))
    targetSeconds = randint(3, maxSeconds)

    now = datetime.now()
    futureTime = now + timedelta(seconds=targetSeconds)
    (time, date) = futureTime.strftime("%H:%M:%S %d/%m/%Y").split(' ')
    return (date, time)


class EventsUI:
    def __init__(self):
        self.eventAsyncIOShit = None
        self.dm = data_manager.DataManager()

    async def init(self, sh_core, startup = False):
        self.sh_core = sh_core
        self.stop()
        convs = self.dm.getConvNames()
        eventList = []
        for c in convs:
            data = self.dm.getRessource(c, "events")
            (newData, evl) = events.getEventList(data, c)
            if startup and not events.checkIfEventExists(newData, "RANDOM_EVENT"):
                # If there is no random event, we add it
                # The funtion addNewRandomEventInQueue already checks the probability value,
                # and if it is 0, it will not add the event.
                await self.addNewRandomEventInQueue(c)
            self.dm.saveRessource(c, "events", newData)
            eventList+=evl

        self.eventAsyncIOShit = asyncioDeepShit.create_task(events.startEventThread(eventList, self.eventCallBack))

    def stop(self):
        if self.eventAsyncIOShit != None:
            try:
                self.eventAsyncIOShit.cancel()
            except:
                print("Fuck asyncio dumb shit")


    async def sendRandomEvent(self, ev_conv):
        r = randint(0, 4)

        respType = ContextualBot.TEXT
        respData = "Mes hommages madame, je suis autiste" # (Faut la ref, sinon c'est chelou)

        # There is a weird bug around the zalgo mode feature.
        # It seems not working if the respData text is too long, but I don't know why...
        # After quick tests, I think the python code is working as expected,
        # but Telegram is removing zalgo characters for whatever reason.
        zalgoMode = (randint(0, 1) == 0)

        speakMode = (randint(0, 1) == 0)


        def truc(respType, respData):
            if speakMode:
                respType = ContextualBot.AUDIO
                languageList = ['af', 'ar', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en-au', 'en-ca', 'en-gb', 'en-gh', 'en-ie', 'en-in', 'en-ng', 'en-nz', 'en-ph', 'en-tz', 'en-uk', 'en-us', 'en-za', 'en', 'eo', 'es-es', 'es-us', 'es', 'et', 'fi', 'fr-ca', 'fr-fr', 'fr', 'gu', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jw', 'km', 'kn', 'ko', 'la', 'lv', 'mk', 'ml', 'mr', 'my', 'ne', 'nl', 'no', 'pl', 'pt-br', 'pt-pt', 'pt', 'ro', 'ru', 'si', 'sk', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-CN', 'zh-cn', 'zh-tw']
                vl = languageList[randint(0, len(languageList)-1)]
                if randint(0, 1) == 0:
                    vl = "fr-FR"
                getVoice2(respData, soundPath+'v.mp3', vl, False)
                respData = soundPath + "v.mp3"
            elif zalgoMode:
                respData = zalgo.zalgo().zalgofy(respData)
            return (respType, respData)


        if r == 0:
            respType = ContextualBot.TEXT
            respData = getRandomWiki()
        elif r == 1:
            respType = ContextualBot.TEXT
            respData = getInfo()
            (respType, respData) = truc(respType, respData)
        elif r == 2:
            respType = ContextualBot.TEXT
            respData = getQuote()
            (respType, respData) = truc(respType, respData)
        elif r == 3:
            respType = ContextualBot.VIDEO
            respData = getRandomVideoURL()
        elif r == 4:
            respType = ContextualBot.AUDIO
            # TODO: find the missing x.wav file
            sound_files = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "d", "d", "r", "c"]
            soundInputText = ''.join([sound_files[randint(0, len(sound_files)-1)] for i in range(randint(4, 10))])
            calculate(soundInputText, soundPath)
            respData = soundPath + "v.mp3"

        if respType == ContextualBot.TEXT:
            await self.sh_core.telegramBot.send_message(ev_conv, respData)
        elif respType == ContextualBot.VIDEO:
            await self.sh_core.telegramBot.send_video(ev_conv, respData)
        elif respType == ContextualBot.AUDIO:
            await self.sh_core.telegramBot.send_audio(ev_conv, open(respData, 'rb'))


    async def eventCallBack(self, ev_conv, ev_txt):
        if (ev_txt == "RANDOM_EVENT"):
            try:
                await self.sendRandomEvent(ev_conv)
            except Exception as e:
                print("Oups: ", e)
            await self.addNewRandomEventInQueue(ev_conv)
        else:
            await self.sh_core.telegramBot.send_message(chat_id=ev_conv, text=ev_txt)

    async def addEvent(self, contextual_bot, sh_core):
        msg = contextual_bot.getText()[7:]
        i0 = msg.find(' ', 0)
        i1 = msg.find(' ', i0+1)
        error_code = 2
        nextTrig = None
        data = self.dm.getRessource(contextual_bot.getChatID(), "events")
        if i0 != -1 and i1 != -1:
            (error_code, nextTrig, newdata) = events.addEvent(data, msg[0:i0], msg[i0+1:i1], msg[i1+1:])
        if error_code == 0:
            contextual_bot.reply(ContextualBot.TEXT, "Prochaine occurence:\n" + str(nextTrig))
            self.dm.saveRessource(contextual_bot.getChatID(), "events", newdata)
            await self.init(self.sh_core)
        else:
            if error_code == 2:
                contextual_bot.reply(ContextualBot.TEXT, "Formattage incorrect")
            elif error_code == -1:
                contextual_bot.reply(ContextualBot.TEXT, "La date est passée tocard")
            elif error_code == 1:
                contextual_bot.reply(ContextualBot.TEXT, "Cette date n'existe pas tocard")
            elif error_code == 4:
                contextual_bot.reply(ContextualBot.TEXT, "Jour de la semaine non reconnu")
            elif error_code >= 10:
                contextual_bot.reply(ContextualBot.TEXT, "Heure invalide")
    async def setMainEvent(self, contextual_bot, sh_core):
        msg = contextual_bot.getText()[11:]
        i0 = msg.find(' ', 0)
        i1 = msg.find(' ', i0+1)
        error_code = 2
        nextTrig = None
        if i0 != -1 and i1 != -1:
            (error_code, nextTrig, newdata) = events.addEvent("", msg[0:i0], msg[i0+1:i1], msg[i1+1:])
        if error_code == 0:
            contextual_bot.reply(ContextualBot.TEXT, "Prochaine occurence:\n" + str(nextTrig))
            self.dm.saveRessource(contextual_bot.getChatID(), "main_event", newdata)
        else:
            if error_code == 2:
                contextual_bot.reply(ContextualBot.TEXT, "Formattage incorrect")
            elif error_code == -1:
                contextual_bot.reply(ContextualBot.TEXT, "La date est passée tocard")
            elif error_code == 1:
                contextual_bot.reply(ContextualBot.TEXT, "Cette date n'existe pas tocard")
            elif error_code == 4:
                contextual_bot.reply(ContextualBot.TEXT, "Jour de la semaine non reconnu")
            elif error_code >= 10:
                contextual_bot.reply(ContextualBot.TEXT, "Heure invalide")
    async def reactMainEvent(self, contextual_bot, sh_core):
        data = self.dm.getRessource(contextual_bot.getChatID(), "main_event")
        (newData, evl) = events.getEventList2(data, contextual_bot.getChatID())
        self.dm.saveRessource(contextual_bot.getChatID(), "main_event", newData)
        if len(evl) != 0:
            (ev_dt, ev_conv, ev_txt) = evl[0]

            # Well, this is just now
            now = datetime.today()

            delta_s = (ev_dt-now).total_seconds()
            (days, hours, minutes, seconds) = getDHMS(delta_s)

            thisIsFineGif = days < 5

            str_output = "Il reste " + smartDayPrintStr(days, hours, minutes, seconds) + " avant " + ev_txt

            # Get main event last time it has been requested
            main_event_last_trigger_date = self.dm.getRessource(contextual_bot.getChatID(), "main_event_lt")
            self.dm.saveRessource(contextual_bot.getChatID(), "main_event_lt", str(now))
            try:
                delta_s = (now-datetime.strptime(main_event_last_trigger_date, "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
            except:
                delta_s = (now-now).total_seconds()
            print(main_event_last_trigger_date, delta_s)
            (days, hours, minutes, seconds) = getDHMS(delta_s)
            str_output += "\nDernière utilisation de la commande: il y a " + smartDayPrintStr(days, hours, minutes, seconds)

            contextual_bot.reply(ContextualBot.TEXT, str_output)
            if thisIsFineGif:
                contextual_bot.reply(ContextualBot.ANIMATION, "https://tenor.com/view/fine-this-is-fine-fine-dog-shaking-intensifies-im-ok-gif-15733726")
            return
        contextual_bot.reply(ContextualBot.TEXT, "Aucun événement majeur en mémoire")




    async def addNewRandomEventInQueue(self, ev_conv):
        parameters = self.sh_core.getParameterList().getConv(ev_conv)
        reParams = parameters.getList("RANDOM_EVENT")
        proba = reParams[0]
        if proba == "":
            proba = "0"
        proba = int(proba)
        data = self.dm.getRessource(ev_conv, "events")
        data = events.removeEventByContent(data, "RANDOM_EVENT")
        if proba > 0:
            (date, time) = getRandomDateTime(proba)
            (error_code, nextTrig, newdata) = events.addEvent(data, date, time, "RANDOM_EVENT")
            # await self.sh_core.telegramBot.send_message(ev_conv, "Prochaine occurence:\n" + str(nextTrig))
        else:
            newdata = data
        self.dm.saveRessource(ev_conv, "events", newdata)
        await self.init(self.sh_core)




    async def configureRandomEvent(self, contextual_bot, sh_core):
        parameters = sh_core.getParameterList().getConv(contextual_bot.getChatID())

        t = contextual_bot.getText().split(' ')
        if len(t) == 2:
            reParams = parameters.getList("RANDOM_EVENT")
            v = -1
            try:
                v = int(t[1])
            except:
                v = int(reParams[0])
            if v >= 0 and v <= 100:
                reParams[0] = str(v)
                parameters.setList("RANDOM_EVENT", reParams)

                # Configure the random event
                await self.addNewRandomEventInQueue(contextual_bot.getChatID())


        reParams = parameters.getList("RANDOM_EVENT")

        contextual_bot.reply(ContextualBot.TEXT, "Random event probability: " + reParams[0] + "%")

