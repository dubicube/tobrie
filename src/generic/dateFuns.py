
def getDHMS(delta_s):
    days = int(delta_s/(24*3600))
    delta_s-=days*24*3600
    hours = int(delta_s/3600)
    delta_s-=hours*3600
    minutes = int(delta_s/60)
    seconds = delta_s-(minutes*60)
    return (days, hours, minutes, seconds)

# POV: Je me fais chier à dev des fonctions totalement inutiles
def smartDayPrintStr(days, hours, minutes, seconds):
    r = []
    if days == 1:
        r += ["1 jour"]
    elif days > 1:
        r += [str(days) + " jours"]
    if hours == 1:
        r += ["1 heure"]
    elif hours > 1:
        r += [str(hours) + " heures"]
    if minutes == 1:
        r += ["1 minute"]
    elif minutes > 1:
        r += [str(minutes) + " minutes"]
    if seconds == 1:
        r += ["1 seconde"]
    elif seconds > 1:
        r += [str(seconds) + " secondes"]

    if len(r) == 0:
        # https://french.stackexchange.com/questions/1975/0-1-et-les-nombres-decimaux-sont-ils-singuliers-ou-pluriels/1977
        return "5.391247x10^-44 seconde" # Yep, this is the Planck time
    elif len(r) == 1:
        return r[0]
    elif len(r) == 2:
        return r[0] + " et " + r[1]
    else:
        return ', '.join(r[:-1]) + " et " + r[-1]

    print("Message à mon moi du futur qui comprendra pas pourquoi j'ai mis ce print qui ne peut jamais être exécuté")
    # Enfin techniquement pas totalement impossible, avec un peu de chance avec les rayons cosmiques...
