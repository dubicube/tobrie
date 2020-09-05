from discord import File as DiscordFile
from generic.audio import *
import random


class ContextualBot:
    TEXT = 0
    DOCUMENT = 1
    VIDEO = 2
    IMAGE = 3
    AUDIO = 4
    STICKER = 5
    ANIMATION = 6
    PIC_LIST = [VIDEO, IMAGE, STICKER, ANIMATION]

    def __init__(self):
        self.type = "None"
        self.reply_queue = []
        self.reply_queue_pic = []
    def getChatID(self):
        return 0
    def getUserID(self):
        return 0
    def getUserName(self):
        return ""
    def getUserFirstName(self):
        return ""
    def isChatPerso(self):
        return False
    def getText(self):
        return ""
    def getAbsoluteText(self):
        return ""
    def reply(self, type, obj, proba=100):
        self.reply_queue+=[(type, obj, proba)]
        if type in ContextualBot.PIC_LIST:
            self.reply_queue_pic+=[(type, obj, proba)]
    def clearQueue(self):
        self.reply_queue = []
        self.reply_queue_pic = []
    def purge(self):
        q = []
        for (type, obj, proba) in self.reply_queue:
            if not type in ContextualBot.PIC_LIST:
                q+=[(type, obj, proba)]
        if len(self.reply_queue_pic) > 0:
            q+=self.reply_queue_pic[random.randint(0, len(self.reply_queue_pic-1))]
        self.reply_queue = q

class TelegramBot(ContextualBot):
    update = None
    context = None
    message = None
    def __init__(self, update, context):
        super(TelegramBot, self).__init__()
        self.update = update
        self.context = context
        if not self.update.message is None:
            self.message = update.message
        if not update.edited_message is None:
            self.message =  update.edited_message
    def getChatID(self):
        return self.message.chat_id
    def getUserID(self):
        return self.message.from_user.id
    def getUserName(self):
        return self.message.from_user.username
    def getUserFirstName(self):
        return self.message.from_user.first_name
    def getAbsoluteText(self):
        if not self.message is None:
            return self.message.text
        else:
            return ""
    def getText(self):
        if not self.update.message is None:
            return self.update.message.text
        else:
            return ""
    def isChatPerso(self):
        return self.message.chat_id == self.message.from_user.id
    def outputMessages(self):
        b = self.context.bot
        funs = [b.send_message, b.send_document, b.send_video, b.send_photo, b.send_audio, b.send_sticker, b.send_animation]
        for (type, obj, proba) in self.reply_queue:
            if type < len(funs) and not type in ContextualBot.PIC_LIST:
                funs[type](self.update.message.chat_id, obj)
        if len(self.reply_queue_pic) > 0:
            proba_total = 0
            for (type, obj, proba) in self.reply_queue_pic:
                proba_total+=proba
            target_proba = random.randint(0, proba_total + (100*len(self.reply_queue_pic)-proba_total)//len(self.reply_queue_pic) - 1)
            if target_proba < proba_total:
                i = 0
                proba_total = 0
                while proba_total <= target_proba:
                    (_, _, proba) = self.reply_queue_pic[i]
                    proba_total+=proba
                    i+=1
                (type, obj, proba) = self.reply_queue_pic[i-1]
                funs[type](self.update.message.chat_id, obj)
        super().clearQueue()


class DiscordBot(ContextualBot):
    message = None
    def __init__(self, message):
        self.message = message
        super(DiscordBot, self).__init__()
    def getChatID(self):
        return 0
    def getUserID(self):
        return self.message.author
    def getUserName(self):
        return self.message.author
    def isChatPerso(self):
        return str(self.message.author)=="dubicube#8553"
    def getText(self):
        return self.message.content
    def getAbsoluteText(self):
        return self.message.content

    async def outputMessages(self):
        super().purge()
        for (type, obj, proba) in self.reply_queue:
            if type==ContextualBot.TEXT or type==ContextualBot.VIDEO or type==ContextualBot.ANIMATION:
                await self.message.channel.send(obj)
            if type==ContextualBot.DOCUMENT or type==ContextualBot.IMAGE or type==ContextualBot.AUDIO:
                await self.message.channel.send(file=DiscordFile(obj))
            if type==ContextualBot.STICKER:
                obj.get_file().download("temp/sticker.webp")
                await self.message.channel.send(file=DiscordFile("temp/sticker.webp"))
        super().clearQueue()


class TweepyBot(ContextualBot):
    api = None
    tweet = None
    def __init__(self, api, tweet):
        super(TweepyBot, self).__init__()
        self.api = api
        self.tweet = tweet
    def getChatID(self):
        return 0
    def getUserID(self):
        return self.tweet.user.id
    def getUserName(self):
        return self.tweet.user.name
    def getText(self):
        return self.tweet.text
    def getAbsoluteText(self):
        return self.tweet.text

    def outputMessages(self):
        super().purge()
        txt_rep = []
        for (type, obj, proba) in self.reply_queue:
            if type == ContextualBot.TEXT or type == ContextualBot.VIDEO:
                txt_rep+=[obj]
        count = len(self.getUserName())+1
        i = 0
        while i < len(txt_rep) and count+len(txt_rep[i])+1 < 280:
            count+=len(txt_rep[i])+1
            i+=1
        if i != 0:
            txt = '\n'.join(txt_rep[:i])
            self.api.update_status("@"+self.getUserName()+" "+txt, self.tweet.id)
            #print("@"+self.getUserName()+" "+txt)
        #for video in self.video_reply:
        #    await self.message.channel.send(video)
        super().clearQueue()

class MailBot(ContextualBot):
    manager = None
    mail = None
    def __init__(self, manager, mail):
        self.manager = manager
        self.mail = mail
        super(MailBot, self).__init__()
    def getUserID(self):
        return self.mail[0]
    def getUserName(self):
        return self.mail[0]
    def getText(self):
        return self.mail[2]
    def getAbsoluteText(self):
        return self.mail[2]

    def outputMessages(self):
        super().purge()
        data = ""
        for (type, obj, proba) in self.reply_queue:
            if type==ContextualBot.TEXT or type==ContextualBot.VIDEO or type==ContextualBot.ANIMATION:
                data+=obj+"\n"
        if len(data) != 0:
            addrs = self.manager.getAddressesToReply(self.mail)
            #print(addrs[0], addrs[1], self.mail[3], data)
            self.manager.send_email(addrs[0], addrs[1], self.mail[3], data)
        super().clearQueue()


class BrendapiBot(ContextualBot):
    data = None
    brendapi = None
    clientsocket = None
    addr = None
    def __init__(self, data, brendapi, clientsocket, addr):
        self.data = data
        self.brendapi = brendapi
        self.clientsocket = clientsocket
        (self.addr, _) = addr
        super(BrendapiBot, self).__init__()
    def getChatID(self):
        return 0
    def getUserID(self):
        return self.addr
    def getUserName(self):
        return self.addr
    def getText(self):
        return self.data
    def getAbsoluteText(self):
        return self.data

    def outputMessages(self):
        super().purge()
        resp = []
        for (type, obj, proba) in self.reply_queue:
            if type==ContextualBot.TEXT or type==ContextualBot.VIDEO or type==ContextualBot.ANIMATION:
                resp+=[obj]
        if len(resp) != 0:
            self.brendapi.send_text('\n'.join(resp), self.clientsocket)
        else:
            self.brendapi.send_text("", self.clientsocket)
        super().clearQueue()


class SpeechBot(ContextualBot):
    update = None
    context = None
    data = None
    def __init__(self, update, context, data):
        self.update = update
        self.context = context
        self.data = data
        super(SpeechBot, self).__init__()
    def getChatID(self):
        return self.update.message.chat_id
    def getUserID(self):
        return self.update.message.from_user.id
    def getUserName(self):
        return self.update.message.from_user.username
    def getUserFirstName(self):
        return self.update.message.from_user.first_name
    def getAbsoluteText(self):
        return self.data
    def getText(self):
        return self.data
    def isChatPerso(self):
        return self.update.message.chat_id == self.update.message.from_user.id
    def outputMessages(self):
        super().purge()
        b = self.context.bot
        funs = [b.send_message, b.send_document, b.send_video, b.send_photo, b.send_audio, b.send_sticker, b.send_animation]
        #all_text = []
        for (type, obj, proba) in self.reply_queue:
            #if type == ContextualBot.TEXT:
            #        all_text+=[obj]
            if type < len(funs):
                funs[type](self.update.message.chat_id, obj)
        #all_text = " ".join(all_text)
        #getVoice(all_text, "temp/out.mp3")
        #b.send_audio(self.update.message.chat_id, open("temp/out.mp3", 'rb'))
        super().clearQueue()
