import os

#videoPath = 'video/'
soundPath = 'sound/'
memePath = 'meme/'
logPath = 'log/'
tempPath = 'temp/'
stickers_map_file = 'maps/sticker_map'
text_map_file = 'maps/text_map'
video_map_file = 'maps/video_map'

dataServerAddress = 'http://copperbot.fr/tobrie_uploader/videos/'
thumbnailsServerAddress = 'http://copperbot.fr/tobrie_uploader/thumbnails/'

regex_start = "(^| |\')("
regex_end = ")($| |,|\\.|!|\\?)"


dataPath = 'data/old/'

users = {'Alban':470589955, 'Mathieu':400322253, 'Vincent':479998987,
        'Emile':938620840, 'Tristan':427032387, 'Leo':936261629,
        'Erwann':893891596, 'Sebastien':902796168, 'Hugo':460908392,
        'Martin':955908707}

admin_user_id = [users['Alban'], users['Vincent']]
super_admin = users['Vincent']

id_test = -1001486633512
id_conv_robot = -1001455757279
id_campagne = -1001445559004
id_petites_loutres = -1001216704238
id_loutres_officielles = -1001403402459
id_first_year = -366419257

id_console = 479998987

conv_perso = 479998987

TEST = not os.path.isdir(logPath)
