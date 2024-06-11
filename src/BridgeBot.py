from enum import IntEnum


###########################################################
#                        MESSAGES                         #
###########################################################


class MessageType(IntEnum):
    # Message is a text message
    TEXT = 0
    # Message is an image
    IMAGE = 1
    # Message is a video
    VIDEO = 2
    # Message is an audio message
    AUDIO = 3
    # Message is a file
    FILE = 4
    # Message is a sticker
    STICKER = 5

class MessageData:
    def __init__(self, messageType=None, text=''):
        self.messageType = messageType
        self.text = text

    def toString(self):
        return '('+str(int(self.messageType))+', '+self.text+')'

    def fromString(self, fstr):
        (i, j) = (1, fstr.find(', ', 0))
        self.messageType = MessageType(int(fstr[i:j]))
        self.text = fstr[j+2:-1]


###########################################################
#                        USERS                            #
###########################################################

class User:
    def __init__(self, firstName='', lastName='', userName='', userId=0):
        self.firstName = firstName
        self.lastName = lastName
        self.userName = userName
        self.userId = userId
    def toString(self):
        params = [str(self.firstName), str(self.lastName), str(self.userName), str(self.userId)]
        return '('+', '.join(params)+')'
    def fromString(self, fstr):
        (i, j) = (1, fstr.find(', ', 0))
        self.firstName = fstr[i:j]
        (i, j) = (j+2, fstr.find(', ', j+2))
        self.lastName = fstr[i:j]
        (i, j) = (j+2, fstr.find(', ', j+2))
        self.userName = fstr[i:j]
        self.userId = int(fstr[j+2:-1])


###########################################################
#                        EVENTS                           #
###########################################################

# The source of events
class EventSource(IntEnum):
    TELEGRAM = 0
    DISCORD = 1
    TWEETER = 2
    MAIL = 3

class EventType(IntEnum):
    # Event is a message received in a chat
    MESSAGE = 0
    # Event is an edited message
    EDITED_MESSAGE = 1
    # Event is a new member joined the chat
    NEW_MEMBER = 2
    # Event is the bot is added to a chat
    NEW_CHAT = 3

class Event:
    def __init__(self, source, chatId, etype, user, data):
        self.source = source
        self.chatId = chatId
        self.etype = etype
        self.user = user
        self.data = data
    def toString(self):
        params = [str(int(self.source)), str(self.chatId), str(int(self.etype)), self.user.toString(), self.data.toString()]
        return '('+', '.join(params)+')'
    def fromString(self, fstr):
        (i, j) = (1, fstr.find(', ', 0))
        self.source = EventSource(int(fstr[i:j]))
        (i, j) = (j+2, fstr.find(', ', j+2))
        self.chatId = int(fstr[i:j])
        (i, j) = (j+2, fstr.find(', (', j+2))
        self.etype = EventType(int(fstr[i:j]))
        (i, j) = (j+3, fstr.find('), (', j+3))
        self.user = User()
        self.user.fromString(fstr[i-1:j+1])
        if self.etype == EventType.MESSAGE:
            self.data = MessageData()
        elif self.etype == EventType.EDITED_MESSAGE:
            self.data = None
        elif self.etype == EventType.NEW_MEMBER:
            self.data = None
        elif self.etype == EventType.NEW_CHAT:
            self.data = None
        self.data.fromString(fstr[j+3:-1])


###########################################################
#                        REPLIES                          #
###########################################################


class Reply:
    def __init__(self, source, chatId, messageType, data=''):
        self.source = source
        self.chatId = chatId
        self.messageType = messageType
        self.data = data
    def toString(self):
        params = [str(int(self.source)), str(self.chatId), str(int(self.messageType)), self.data]
        return '('+', '.join(params)+')'
    def fromString(self, fstr):
        (i, j) = (1, fstr.find(', ', 0))
        self.source = EventSource(int(fstr[i:j]))
        (i, j) = (j+2, fstr.find(', ', j+2))
        self.chatId = int(fstr[i:j])
        (i, j) = (j+2, fstr.find(', ', j+2))
        self.messageType = MessageType(int(fstr[i:j]))
        self.data = fstr[j+2:-1]
