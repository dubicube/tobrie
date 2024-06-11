from BridgeBot import *

user = User('John', 'Doe', 'jdoe', 12345)
fstr0 = user.toString()
user.fromString(fstr0)
fstr1 = user.toString()
if fstr0 != fstr1:
    print('USER FAILED:')
    print(fstr0)
    print(fstr1)
else:
    print('USER PASSED')

messageData = MessageData(MessageType.TEXT, 'Hello, World!')
fstr0 = messageData.toString()
messageData.fromString(fstr0)
fstr1 = messageData.toString()
if fstr0 != fstr1:
    print('MESSAGEDATA FAILED:')
    print(fstr0)
    print(fstr1)
else:
    print('MESSAGEDATA PASSED')

event = Event(EventSource.TELEGRAM, 123456, EventType.MESSAGE, User('John', 'Doe', 'jdoe', 12345), MessageData(MessageType.TEXT, 'Hello, world!'))
fstr0 = event.toString()
event.fromString(fstr0)
fstr1 = event.toString()
if fstr0 != fstr1:
    print('EVENT FAILED:')
    print(fstr0)
    print(fstr1)
else:
    print('EVENT PASSED')


event = Event(EventSource.TELEGRAM, -123456, EventType.MESSAGE, User('John', 'Doe', 'jdoe', 12345), MessageData(MessageType.TEXT, 'est(")" lol, krj,h\'lkj)\'fk'))
fstr0 = event.toString()
event.fromString(fstr0)
fstr1 = event.toString()
if fstr0 != fstr1:
    print('EVENT2 FAILED:')
    print(fstr0)
    print(fstr1)
else:
    print('EVENT2 PASSED')

reply = Reply(EventSource.TELEGRAM, 456789, MessageType.TEXT, 'Hello, world!')
fstr0 = reply.toString()
reply.fromString(fstr0)
fstr1 = reply.toString()
if fstr0 != fstr1:
    print('REPLY FAILED:')
    print(fstr0)
    print(fstr1)
else:
    print('REPLY PASSED')