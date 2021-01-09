import datetime

import data_manager
import events
from contextual_bot import *


class EventsUI:
    def __init__(self):
        self.dm = data_manager.DataManager()

    def init(self, sh_core):
        self.sh_core = sh_core
        events.stopEventThread()
        convs = self.dm.getConvNames()
        eventList = []
        for c in convs:
            data = self.dm.getRessource(c, "events")
            (newData, evl) = events.getEventList(data, c)
            self.dm.saveRessource(c, "events", newData)
            eventList += evl
        events.startEventThread(eventList, self.eventCallBack)

    def stop(self):
        events.stopEventThread()

    def eventCallBack(self, ev_conv, ev_txt):
        try:
            self.sh_core.telegramBot.send_message(chat_id=ev_conv, text=ev_txt)
        except:
            print(ev_conv, ev_txt)

    def addEvent(self, contextual_bot, sh_core):
        msg = contextual_bot.getText()[7:]
        i0 = msg.find(" ", 0)
        i1 = msg.find(" ", i0 + 1)
        error_code = 2
        nextTrig = None
        data = self.dm.getRessource(contextual_bot.getChatID(), "events")
        if i0 != -1 and i1 != -1:
            (error_code, nextTrig, newdata) = events.addEvent(
                data, msg[0:i0], msg[i0 + 1 : i1], msg[i1 + 1 :]
            )
        if error_code == 0:
            contextual_bot.reply(
                ContextualBot.TEXT, "Prochaine occurence:\n" + str(nextTrig)
            )
            self.dm.saveRessource(contextual_bot.getChatID(), "events", newdata)
            self.init(self.sh_core)
        else:
            if error_code == 2:
                contextual_bot.reply(ContextualBot.TEXT, "Formattage incorrect")
            elif error_code == -1:
                contextual_bot.reply(ContextualBot.TEXT, "La date est passée tocard")
            elif error_code == 1:
                contextual_bot.reply(
                    ContextualBot.TEXT, "Cette date n'existe pas tocard"
                )
            elif error_code == 4:
                contextual_bot.reply(
                    ContextualBot.TEXT, "Jour de la semaine non reconnu"
                )
            elif error_code >= 10:
                contextual_bot.reply(ContextualBot.TEXT, "Heure invalide")

    def setMainEvent(self, contextual_bot, sh_core):
        msg = contextual_bot.getText()[11:]
        i0 = msg.find(" ", 0)
        i1 = msg.find(" ", i0 + 1)
        error_code = 2
        nextTrig = None
        if i0 != -1 and i1 != -1:
            (error_code, nextTrig, newdata) = events.addEvent(
                "", msg[0:i0], msg[i0 + 1 : i1], msg[i1 + 1 :]
            )
        if error_code == 0:
            contextual_bot.reply(
                ContextualBot.TEXT, "Prochaine occurence:\n" + str(nextTrig)
            )
            self.dm.saveRessource(contextual_bot.getChatID(), "main_event", newdata)
        else:
            if error_code == 2:
                contextual_bot.reply(ContextualBot.TEXT, "Formattage incorrect")
            elif error_code == -1:
                contextual_bot.reply(ContextualBot.TEXT, "La date est passée tocard")
            elif error_code == 1:
                contextual_bot.reply(
                    ContextualBot.TEXT, "Cette date n'existe pas tocard"
                )
            elif error_code == 4:
                contextual_bot.reply(
                    ContextualBot.TEXT, "Jour de la semaine non reconnu"
                )
            elif error_code >= 10:
                contextual_bot.reply(ContextualBot.TEXT, "Heure invalide")

    def reactMainEvent(self, contextual_bot, sh_core):
        data = self.dm.getRessource(contextual_bot.getChatID(), "main_event")
        (newData, evl) = events.getEventList2(data, contextual_bot.getChatID())
        self.dm.saveRessource(contextual_bot.getChatID(), "main_event", newData)
        if len(evl) != 0:
            (ev_dt, ev_conv, ev_txt) = evl[0]
            delta_s = (ev_dt - datetime.datetime.today()).total_seconds()
            days = int(delta_s / (24 * 3600))
            delta_s -= days * 24 * 3600
            hours = int(delta_s / 3600)
            delta_s -= hours * 3600
            minutes = int(delta_s / 60)
            seconds = delta_s - (minutes * 60)
            contextual_bot.reply(
                ContextualBot.TEXT,
                "Il reste "
                + str(days)
                + " jours, "
                + str(hours)
                + " heures, "
                + str(minutes)
                + " minutes et "
                + str(seconds)
                + " secondes avant "
                + ev_txt,
            )
            return
        contextual_bot.reply(ContextualBot.TEXT, "Aucun événement majeur en mémoire")
