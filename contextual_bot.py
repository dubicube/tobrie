from discord import File as DiscordFile


class ContextualBot:
    TEXT = 0
    DOCUMENT = 1
    VIDEO = 2
    IMAGE = 3
    AUDIO = 4
    STICKER = 5
    ANIMATION = 6

    type = "None"
    reply_queue = []
    def __init__(self):
        self.type = "None"
        self.reply_queue = []
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
    def reply(self, type, obj):
        self.reply_queue+=[(type, obj)]

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
        for (type, obj) in self.reply_queue:
            if type < len(funs):
                funs[type](self.update.message.chat_id, obj)


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
        for (type, obj) in self.reply_queue:
            if type==ContextualBot.TEXT or type==ContextualBot.VIDEO:
                await self.message.channel.send(obj)
            if type==ContextualBot.DOCUMENT or type==ContextualBot.IMAGE or type==ContextualBot.AUDIO:
                await self.message.channel.send(file=DiscordFile(obj))
            if type==ContextualBot.STICKER:
                obj.get_file().download("sticker.webp")
                await self.message.channel.send(file=DiscordFile("sticker.webp"))


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
        txt_rep = []
        for (type, obj) in self.reply_queue:
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
