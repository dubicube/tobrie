from config import *
from generic.audio import *
from os.path import exists
import os

MORSE_CODE_DICT = { 'A':'.-',     'B':'-...',
                    'C':'-.-.',   'D':'-..',    'E':'.',
                    'F':'..-.',   'G':'--.',    'H':'....',
                    'I':'..',     'J':'.---',   'K':'-.-',
                    'L':'.-..',   'M':'--',     'N':'-.',
                    'O':'---',    'P':'.--.',   'Q':'--.-',
                    'R':'.-.',    'S':'...',    'T':'-',
                    'U':'..-',    'V':'...-',   'W':'.--',
                    'X':'-..-',   'Y':'-.--',   'Z':'--..',
                    '1':'.----',  '2':'..---',  '3':'...--',
                    '4':'....-',  '5':'.....',  '6':'-....',
                    '7':'--...',  '8':'---..',  '9':'----.',
                    '0':'-----',  ',':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.',  '-':'-....-',
                    '(':'-.--.',  ')':'-.--.-'}


morse_timing = 5000

def encrypt(message):
    cipher = ''
    for letter in message:
        if letter != ' ':
            cipher += MORSE_CODE_DICT[letter] + ' '
        else:
            cipher += '|'
    return cipher

def decrypt(message):
    message += ' '
    decipher = ''
    citext = ''
    for letter in message:
        if (letter != ' '):
            i = 0
            citext += letter
        else:
            i += 1
            if i == 2 :
                decipher += ' '
            else:
                decipher += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT.values()).index(citext)]
                citext = ''
    return decipher

def getTiming(message):
    data = encrypt(message.upper())
    result = []
    for c in data:
        if c == '.':
            result+=[[1, 1]]
        elif c == '-':
            result+=[[3, 1]]
        elif c == ' ':
            result[-1][1]=3
        elif c == '|':
            result[-1][1]=7
    return result

def MSR_init():
    MSR_updateFiles()

def MSR_config(fpath, msgtext):
    global morse_timing
    if '.' in msgtext:
        if exists(tempPath + 'morse0.wav'):
            os.remove(tempPath + 'morse0.wav')
        os.rename(fpath, tempPath + 'morse0.wav')
    if '-' in msgtext or '_' in msgtext:
        if exists(tempPath + 'morse1.wav'):
            os.remove(tempPath + 'morse1.wav')
        os.rename(fpath, tempPath + 'morse1.wav')

def MSR_cancer(message):
    pattern = getTiming(message.upper())
    duplicateAudioForMorse(tempPath+'morse0.wav', tempPath+'morse1.wav', tempPath+'v.wav', pattern, morse_timing)
    convertAudioFile(tempPath+'v.wav', tempPath+'v.mp3')
    return tempPath+'v.mp3'


# message = "YOUSK2"
# result = encrypt(message.upper())
# print(result)
#
# message = "--. . . -.- ... -....- ..-. --- .-. -....- --. . . -.- ... "
# result = decrypt(message)
# print(result)
