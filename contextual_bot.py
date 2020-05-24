


class ContextualBot:
    type = "None"
    def __init__(self):
        self.type = "None"
    def getChatID(self):
        return 0
    def getUserID(self):
        return 0
    def getUserName(self):
        return ""
    def getUserFirstName(self):
        return ""
    def isChatPerso(self):
        return True
    def getText(self):
        return ""
    def getAbsoluteText(self):
        return ""
    def replyText(self, text):
        print(text)
    def replyDocument(self, document_url):
        print(gif_url)
    def replyVideo(self, video_url):
        print(video_url)
    def replySticker(self, sticker):
        print("Sticker")
    def replyAnimation(self, animation):
        print("Animation")

class TelegramBot(ContextualBot):
    update = None
    context = None
    message = None
    def __init__(self, update, context):
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
    def replyText(self, text):
        self.context.bot.send_message(self.update.message.chat_id, text)
    def replyDocument(self, document_url):
        self.context.bot.send_document(self.update.message.chat_id, document_url)
    def replyVideo(self, video_url):
        self.context.bot.send_video(self.update.message.chat_id, video_url, supports_streaming=True)
    def replySticker(self, sticker):
        self.context.bot.send_sticker(self.update.message.chat_id, sticker)
    def replyAnimation(self, animation):
        self.context.bot.send_animation(self.update.message.chat_id, animation)



class DiscordBot(ContextualBot):
    message = None
    text_reply = []
    document_reply = []
    video_reply = []
    def __init__(self, message):
        self.message = message
        self.text_reply = []
        self.document_reply = []
        self.video_reply = []
    def getChatID(self):
        return 0
    def getUserID(self):
        return self.message.author
    def getUserName(self):
        return self.message.author
    #def getUserFirstName(self):
    def isChatPerso(self):
        return self.message.author=="dubicube#8553"
    def getText(self):
        return self.message.content
    def getAbsoluteText(self):
        return self.message.content

    def replyText(self, text):
        self.text_reply+=[text]
    def replyDocument(self, document_url):
        self.document_reply+=[document_url]
    def replyVideo(self, video_url):
        self.video_reply+=[video_url]
    def replySticker(self, sticker):
        print("Sticker")
    def replyAnimation(self, animation):
        print("Animation")

    async def outputMessages(self):
        for text in self.text_reply:
            await self.message.channel.send(text)
        for video in self.video_reply:
            await self.message.channel.send(video)
