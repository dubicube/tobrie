from discord import File as DiscordFile
from generic.audio import *
import random
import coin

class ContextualBot:
    TEXT = 0
    DOCUMENT = 1
    VIDEO = 2
    IMAGE = 3
    AUDIO = 4
    STICKER = 5
    CHAINED_STICKERS = 7
    ANIMATION = 6
    PIC_LIST = [VIDEO, IMAGE, STICKER, ANIMATION, CHAINED_STICKERS]

    # Le fromage

    def __init__(self):
        self.type = "None"
        self.reply_queue = []
        self.reply_queue_pic = []
        self.achievement_queue = []
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
    # Returns text of message which the current message is replying to
    def getReplyText(self):
        return ""
    # Returns audio of message which the current message is replying to.
    # Returns a string which is a local path to the downloaded audio file.
    def getReplyAudioFile(self):
        return ""
    # Returns sticker file_id of message which the current message is replying to
    # Return value is a string.
    def getReplySticker(self):
        return ""
    # Returns video file_id of message which the current message is replying to
    def getReplyVideo(self):
        return ""
    async def downloadReplyDocument(self, dirPath):
        return ""
    def reply(self, type, obj, proba=100):
        self.reply_queue+=[(type, obj, proba)]
        if type in ContextualBot.PIC_LIST:
            self.reply_queue_pic+=[(type, obj, proba)]
    def addAchievement(self, type, obj):
        self.achievement_queue+=[(type, obj)]
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
    def removeBotID(self, m):
        t = m.text
        i = 0
        while i<len(t) and t[i] != ' ':
            i+=1
        if i-len(telegram_id) > 0 and t[i-len(telegram_id):i] == telegram_id:
            t = t[:i-len(telegram_id)] + t[i:]
        return t
    def getAbsoluteText(self):
        if not self.message is None:
            return self.removeBotID(self.message)
        else:
            return ""
    def getText(self):
        if not self.update.message is None:
            return self.removeBotID(self.update.message)
        else:
            return ""
    def getReplyAudioFile(self):
        if self.message.reply_to_message == None or self.message.reply_to_message.audio == None:
            return ""
        else:
            fname = self.message.reply_to_message.audio.file_name
            fpath = ''
            if fname.endswith('.wav'):
                fpath = tempPath + 'morse.wav'
            if fname.endswith('.mp3'):
                fpath = tempPath + 'morse.mp3'
            if fpath != '':
                self.message.reply_to_message.audio.get_file().download(fpath)
                return fpath
            return ''
    def getReplySticker(self):
        if self.message.reply_to_message == None or self.message.reply_to_message.sticker == None:
            return ""
        else:
            return str(self.message.reply_to_message.sticker.file_id)
    def getReplyVideo(self):
        if self.message.reply_to_message == None or self.message.reply_to_message.video == None:
            return ""
        else:
            return str(self.message.reply_to_message.video.file_id)
    async def downloadReplyDocument(self, dirPath):
        if self.message.reply_to_message == None or self.message.reply_to_message.document == None:
            return ""
        else:
            path = dirPath + self.message.reply_to_message.document.file_name
            await self.message.reply_to_message.document.get_file().download_to_drive(path)
            return path
    def getReplyText(self):
        if self.message.reply_to_message == None or self.message.reply_to_message.text == None:
            return ""
        else:
            return self.message.reply_to_message.text
    def isChatPerso(self):
        return self.message.chat_id == self.message.from_user.id
    async def send_chained_stickers(self, conv, l):
        for i in l:
            await self.context.bot.send_sticker(conv, i)

    # TODO: dissociate the probability system from the direct message output.
    # The problem with current implementation is that probability is computed at the same time
    # with message output, and thus achievements and coins cannot be easily calculated on other platforms.
    async def outputMessages(self):
        b = self.context.bot
        funs = [b.send_message, b.send_document, b.send_video, b.send_photo, b.send_audio, b.send_sticker, b.send_animation, self.send_chained_stickers]
        for (type, obj, proba) in self.reply_queue:
            if type < len(funs) and not type in ContextualBot.PIC_LIST:
                await funs[type](self.update.message.chat_id, obj)
                coin.increaseUserCoinsFromMessage(self.getChatID(), self.getUserID(), type, obj)
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
                await funs[type](self.update.message.chat_id, obj)
                coin.increaseUserCoinsFromMessage(self.getChatID(), self.getUserID(), type, obj)
        super().clearQueue()
        for (type, obj) in self.achievement_queue:
            await funs[type](self.update.message.chat_id, obj)
            coin.increaseUserCoinsFromMessage(self.getChatID(), self.getUserID(), type, obj)


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
            if type==ContextualBot.CHAINED_STICKERS:
                for o in obj:
                    o.get_file().download("temp/sticker.webp")
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

class SpeechBot2(TelegramBot):
    def __init__(self, update, context, data):
        self.update = update
        self.context = context
        self.data = data
        super(SpeechBot2, self).__init__(update, context)
    def getAbsoluteText(self):
        return self.data
    def getText(self):
        return self.data
