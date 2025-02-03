import datetime
import asyncio as asyncioDeepShit
import events
import data_manager
from contextual_bot import *

def getDHMS(delta_s):
    days = int(delta_s/(24*3600))
    delta_s-=days*24*3600
    hours = int(delta_s/3600)
    delta_s-=hours*3600
    minutes = int(delta_s/60)
    seconds = delta_s-(minutes*60)
    return (days, hours, minutes, seconds)

# POV: Je me fais chier à dev des fonctions totalement inutiles
def smartDayPrintStr(days, hours, minutes, seconds):
    r = []
    if days == 1:
        r += ["1 jour"]
    elif days > 1:
        r += [str(days) + " jours"]
    if hours == 1:
        r += ["1 heure"]
    elif hours > 1:
        r += [str(hours) + " heures"]
    if minutes == 1:
        r += ["1 minute"]
    elif minutes > 1:
        r += [str(minutes) + " minutes"]
    if seconds == 1:
        r += ["1 seconde"]
    elif seconds > 1:
        r += [str(seconds) + " secondes"]

    if len(r) == 0:
        # https://french.stackexchange.com/questions/1975/0-1-et-les-nombres-decimaux-sont-ils-singuliers-ou-pluriels/1977
        return "5.391247x10^-44 seconde" # Yep, this is the Planck time
    elif len(r) == 1:
        return r[0]
    elif len(r) == 2:
        return r[0] + " et " + r[1]
    else:
        return ', '.join(r[:-1]) + " et " + r[-1]

    print("Message à mon moi du futur qui comprendra pas pourquoi j'ai mis ce print qui ne peut jamais être exécuté")
    # Enfin techniquement pas totalement impossible, avec un peu de chance avec les rayons cosmiques...

class EventsUI:
    def __init__(self):
        self.eventAsyncIOShit = None
        self.dm = data_manager.DataManager()

    async def init(self, sh_core):
        self.sh_core = sh_core
        self.stop()
        convs = self.dm.getConvNames()
        eventList = []
        for c in convs:
            data = self.dm.getRessource(c, "events")
            (newData, evl) = events.getEventList(data, c)
            self.dm.saveRessource(c, "events", newData)
            eventList+=evl

        self.eventAsyncIOShit = asyncioDeepShit.create_task(events.startEventThread(eventList, self.eventCallBack))

    def stop(self):
        if self.eventAsyncIOShit != None:
            try:
                self.eventAsyncIOShit.cancel()
            except:
                print("Fuck asyncio dumb shit")


    async def eventCallBack(self, ev_conv, ev_txt):
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
            now = datetime.datetime.today()

            delta_s = (ev_dt-now).total_seconds()
            (days, hours, minutes, seconds) = getDHMS(delta_s)

            thisIsFineGif = days < 5

            str_output = "Il reste " + smartDayPrintStr(days, hours, minutes, seconds) + " avant " + ev_txt

            # Get main event last time it has been requested
            main_event_last_trigger_date = self.dm.getRessource(contextual_bot.getChatID(), "main_event_lt")
            self.dm.saveRessource(contextual_bot.getChatID(), "main_event_lt", str(now))
            try:
                delta_s = (now-datetime.datetime.strptime(main_event_last_trigger_date, "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
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
