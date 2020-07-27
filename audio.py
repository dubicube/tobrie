#########################################################################################
#                                        AUDIO                                          #
#########################################################################################

import wave
import subprocess
import requests
from urllib.request import urlopen
import time
import os
import speech_recognition as sr
from config import *

def speechToText(file, language = "fr-FR"):
    if os.path.isfile("temp/out.wav"):
        os.remove("temp/out.wav")
    os.system(ffmpeg_path+" -i "+file+" temp/out.wav")
    r = sr.Recognizer()
    # open the file
    with sr.AudioFile("temp/out.wav") as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        return r.recognize_google(audio_data, language = language)


# Generate MP3 from text
def getVoice(text, file, language = "fr-FR"):
    url = "http://api.soundoftext.com/sounds"
    data = {"engine":"Google","data":{"text": text,"voice":language}}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'User-Agent': 'Mozilla/5.0'}
    req = requests.post(url, json=data, headers=headers)
    id = req.json()['id']
    url = 'https://soundoftext.nyc3.digitaloceanspaces.com/' + id + '.mp3'
    time.sleep(1)
    filedata = urlopen(url)
    datatowrite = filedata.read()
    with open(file, 'wb') as f:
        f.write(datatowrite)

# Concatenate audio files to convert text operation to audio (from ytp Tintin)
def calculate(input_data, soundPath):
    sound_files = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "x", "d", "r", "c"]
    infiles = []
    for c in input_data:
        if c == '/':c = 'd'
        if c == '*':c = 'x'
        if c in sound_files:
            infiles+=[soundPath+c+".wav"]
    outfile = soundPath+"v.wav"
    data= []
    for infile in infiles:
        w = wave.open(infile, 'rb')
        data.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()

    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(infiles)):
        output.writeframes(data[i][1])
    output.close()
    wav = outfile
    cmd = 'lame --preset insane %s' % wav
    subprocess.call(cmd, shell=True)

# Take the audio file input, and duplicate it v times in the file outfile
def duplicateAudio(input, outfile, v):
    infiles = []
    for i in range(v):
        infiles+=[input]
    data = []
    for infile in infiles:
        w = wave.open(infile, 'rb')
        data.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()

    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(infiles)):
        output.writeframes(data[i][1])
    output.close()
    wav = outfile
    cmd = 'lame --preset insane %s' % wav
    subprocess.call(cmd, shell=True)
