from random import randint
import requests
import youtube_dl
import os

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
}

class YTVideo:
    id = None
    url = None
    def __init__(self, s):
        if s.startswith('https://www.youtube.com/'):
            self.url = s
        else:
            self.id = s
    def getURL(self):
        if self.url == None:
            return 'https://www.youtube.com/watch?v='+self.id
        else:
            return self.url
    def download(self, file):
        if os.path.isfile(file):
            os.remove(file)
        ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': file
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.getURL()])
    def getStreamURL(self):
        with youtube_dl.YoutubeDL(YTDL_OPTS) as ydl:
            video = self._get_info(self.getURL())
            video_format = video["formats"][0]
            #self.stream_url = video_format["url"]
            #self.video_url = video["webpage_url"]
            #self.title = video["title"]
            #self.uploader = video["uploader"] if "uploader" in video else ""
            #self.thumbnail = video["thumbnail"] if "thumbnail" in video else None
            return video_format["url"]
    def _get_info(self, video_url):
        with youtube_dl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"])  # get info for first video
            else:
                video = info
            return video

class MusicQueue:
    queue = []
    playlist = None
    def __init__(self):
        self.queue = []
        self.playlist = None
    def add(self, data):
        data_l = data.lower()
        if data_l == 'eirbot':
            data = Playlist.EIRBOT
        elif data_l == 'eirboom':
            data = Playlist.EIRBOOM
        elif data_l == 'weabot':
            data = Playlist.WEABOT
        elif not data.startswith('https://www.youtube.com/'):
            return (True, 0)
        if data.startswith('https://www.youtube.com/playlist'):
            self.playlist = Playlist(data)
            self.queue+=[YTVideo(i) for i in self.playlist.id_list]
            return (self.playlist.updated, self.playlist.size)
        else:
            self.playlist = None
            self.queue+=[YTVideo(data)]
            return (True, 1)
    def updatePlaylist(self):
        if self.playlist != None:
            self.queue = self.queue[0:-self.playlist.size]
            self.playlist.update()
            self.queue+=[YTVideo(i) for i in self.playlist.id_list]
    def clear(self):
        self.queue = []
        self.playlist = None
    def shuffle(self):
        self.playlist = None
        for i in range(len(self.queue)-2):
            j = randint(i+1, len(self.queue)-1)
            v = self.queue[i]
            self.queue[i] = self.queue[j]
            self.queue[j] = v

class Playlist:
    EIRBOT = 'https://www.youtube.com/playlist?list=PLCQolDsR1jjGI_ZPwxH9uJIvjECZ1-pDA'
    EIRBOOM= 'https://www.youtube.com/playlist?list=PLCQolDsR1jjFRk9cEoq9tnNmJ_i1eqMqh'
    WEABOT = 'https://www.youtube.com/playlist?list=PLCQolDsR1jjHVbGcnf72N_nHPE8uPOJ9e'

    repo_path = "temp/"

    id_list = []
    title = ""
    url = ""
    size = 0
    updated = False

    def __init__(self, url):
        self.url = url
        id = self.__getPlaylistID()
        try:
            f = open(self.repo_path+id, "r")
        except FileNotFoundError:
            self.update()
        else:
            f.close()
            self.__loadFromFile(self.repo_path+id)

    def update(self):
        self.__loadYTPlaylist2(self.url)
        self.__saveToFile(self.repo_path+self.__getPlaylistID())

    def __saveToFile(self, file):
        f = open(file, "w")
        f.write(self.title+"\n")
        f.write(self.url+"\n")
        f.write(str(self.size)+"\n")
        for i in self.id_list:
            f.write(i+"\n")
        f.close()

    def __loadFromFile(self, file):
        f = open(file, "r")
        self.title = f.readline()[:-1]
        self.url = f.readline()[:-1]
        self.size = int(f.readline()[:-1])
        self.id_list = []
        for i in range(self.size):
            self.id_list += [f.readline()[:-1]]
        f.close()

    def __getPlaylistID(self):
        return self.url[38:]

    def __extractID_aux0(self, text, start, nbr=199):
        l = []
        pattern = 'data-video-id="'
        i = start
        for read_cursor in range(nbr):
            i = text.find(pattern, i)+len(pattern)
            j = text.find('"', i+1)
            if i!=-1 and j!=-1:
                if ' ' in text[i:j]:
                    return (-1, [])
                l+=[text[i:j]]
            else:
                print("Error")
        return (i, l)
    def __extractID_aux1(self, playlist_url, video_id, offset=0, nbr=199):
        l = []
        i = -1
        # Basically we have 1 chance over 2 to have a special response
        # that this parser cannot handle.
        # We loop while we don't have a "good" response
        while i==-1:
            text = requests.get('https://www.youtube.com/watch?v='+video_id+'&'+playlist_url[33:]).text
            i = text.find('<ol id="playlist-autoscroll-list"')
            if offset!=0:
                (i, _) = self.__extractID_aux0(text, i, offset)
            if i!=-1:
                (i, l) = self.__extractID_aux0(text, i, nbr)
            if i==-1:
                print("fail")
        return l
    # Get a list with all the ID of the videos in the playlist (no size limit)
    def __loadYTPlaylist(self, playlist_url):
        self.url = playlist_url

        # Get playlist size
        playlist_size = 'E'
        loop = True
        while loop:
            text = requests.get(self.url).text
            i = text.find(' vidéos</li><li>')
            j = i
            while(text[j-1] != '>'):j-=1
            playlist_size = text[j:i].replace(' ', '')
            try:
                playlist_size = int(playlist_size)
                loop = False
            except ValueError:
                loop = True
        self.size = playlist_size

        # Get title
        i = text.find('<title>')
        j = text.find('</title>')
        self.title = text[i+7:j]

        # Get videos ID
        pattern = '<meta property="og:image" content="https://i.ytimg.com/vi/'
        i = text.find(pattern)+len(pattern)
        j = text.find('/', i+1)
        first_video_id = text[i:j]
        l = []
        if playlist_size<=200:
            l = self.__extractID_aux1(self.url, first_video_id, 0, playlist_size)
        else:
            l = self.__extractID_aux1(self.url, first_video_id, 0, 200)
            print(l[0])
            print(l[-1])
            i = 200
            while i+199<=playlist_size:
                l+=self.__extractID_aux1(self.url, l[-1], 200+(1 if i!=200 else 0), 199)
                print(l[-1])
                i+=199
            if i!=playlist_size:
                l+=self.__extractID_aux1(self.url, l[-1], 200+(1 if i!=200 else 0), playlist_size-i)
                print(l[-1])
        self.id_list = l
        self.updated = True
    def __loadYTPlaylist2(self, playlist_url):
        os.system("youtube-dl -j --flat-playlist --ignore-errors "+playlist_url+" | sed '/Private video/d' | jq -r '.id' > temp/rawplaylist")
        f = open("temp/rawplaylist", "r")
        self.id_list = f.read().split('\n')[:-1]
        f.close()
        os.remove("temp/rawplaylist")
        self.updated = True
        self.size = len(self.id_list)
        self.title = "Titre"
