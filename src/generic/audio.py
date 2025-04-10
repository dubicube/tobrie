#########################################################################################
#                                        AUDIO                                          #
#########################################################################################

from gtts import gTTS
import wave
import subprocess
import requests
from urllib.request import urlopen
import time
import os
import speech_recognition as sr
from config import *



def convertAudioFile(input_file, output_file):
    subprocess.call(['ffmpeg', '-y', '-i', input_file, output_file])

def download_file(url, path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)
        return True
    else:
        return False

# Download a sound based on search_data
# Return False if no sound was found
def getSound(search_data, file, index):
    search_url = 'https://www.myinstants.com/search/?name='+'+'.join(search_data.split(' '))
    text = requests.get(search_url).text
    i = 0
    for j in range(index+1):
        i = text.find('onclick="play(\'', i+1)
        if i==-1:return False
    j = text.find('\'', i+20)
    if j==-1:return False
    sound_url = 'https://www.myinstants.com/' + text[i+16:j]
    f = download_file(sound_url, file)
    return f

def speechToText(file, language = "fr-FR"):
    if os.path.isfile(tempPath+"out.wav"):
        os.remove(tempPath+"out.wav")
    os.system(ffmpeg_path+" -i "+file+" "+tempPath+"out.wav")
    r = sr.Recognizer()
    # open the file
    with sr.AudioFile(tempPath+"out.wav") as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        return r.recognize_google(audio_data, language = language)


def getVoice2(text, file, language = "fr-FR", slow=False):
    gTTS(text=text, lang=language, slow=slow).save(file)

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

def appendAudioFiles(fileList, outfile):
    data = []
    frameLength = 0
    for infile in fileList:
        w = wave.open(infile, 'rb')
        frameLength = len(w.readframes(1))
        data.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()

    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(fileList)):
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
    appendAudioFiles(infiles, outfile)

def duplicateAudioForMorse(input0, input1, outfile, pattern, timing):
    w = wave.open(input0, 'rb')
    frameLength = len(w.readframes(1))
    data0 = [w.getparams(), w.readframes(w.getnframes())]
    fr = w.getframerate()
    w.close()
    w = wave.open(input1, 'rb')
    data1 = [w.getparams(), w.readframes(w.getnframes())]
    w.close()

    output = wave.open(outfile, 'wb')
    output.setparams(data0[0])
    for i in range(len(pattern)):
        if pattern[i][0] == 1:
            output.writeframes(data0[1])
        else:
            output.writeframes(data1[1])
        emptyspace = bytes((pattern[i][1]*frameLength*timing)*[0])
        output.writeframes(emptyspace)
    output.close()
    wav = outfile
    cmd = 'lame --preset insane %s' % wav
    subprocess.call(cmd, shell=True)
