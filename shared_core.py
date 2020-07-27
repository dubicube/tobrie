from datetime import datetime
from config import *

class SharedCore:
    def __init__(self, telegramBot, remote_service):
        self.telegramBot = telegramBot
        self.remote_service = remote_service
    def saveToLog(self, contextual_bot):
        if not TEST:
            file = open(logPath+str(contextual_bot.getChatID()),"a")
            file.write("["+contextual_bot.getUserFirstName()+", "+str(contextual_bot.getUserID())+", "+str(datetime.now())+": "+contextual_bot.getAbsoluteText()+"\n")
            file.close()
    def notifConsole(self, contextual_bot):
        text = "["+str(contextual_bot.getChatID())+", "+contextual_bot.getUserFirstName()+", "+str(contextual_bot.getUserID())+": "+contextual_bot.getAbsoluteText()
        self.telegramBot.send_message(chat_id=conv_perso, text=text)
