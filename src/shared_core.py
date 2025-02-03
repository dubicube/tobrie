from datetime import datetime
from config import *
from contextual_bot import *
from conv_parameter import *
import IDLogger
import data_manager

class SharedCore:
    def __init__(self, telegramBot, remote_service):
        self.telegramBot = telegramBot
        self.remote_service = remote_service
        self.data_manager = data_manager.DataManager()
        self.conv_parameter_list = ConvParameterList()
    def saveToLog(self, contextual_bot):
        if not TEST:
            file = open(logPath+str(contextual_bot.getChatID()),"a")
            file.write("["+contextual_bot.getUserFirstName()+", "+str(contextual_bot.getUserID())+", "+str(datetime.now())+": "+contextual_bot.getAbsoluteText()+"\n")
            file.close()
    async def notifConsole(self, contextual_bot, text = ""):
        #if isinstance(contextual_bot, TelegramBot):
        #    IDLogger.addUser(self.telegramBot, self.data_manager, contextual_bot.getChatID(), contextual_bot.getUserID())
        if text == "":
            text = "["+str(contextual_bot.getChatID())+", "+contextual_bot.getUserFirstName()+", "+str(contextual_bot.getUserID())+": "+contextual_bot.getAbsoluteText()
        if len(text) > 4096:
            text = text[:4096]
        await self.telegramBot.send_message(chat_id=conv_perso, text=text)
    def getParameterList(self):
        return self.conv_parameter_list
