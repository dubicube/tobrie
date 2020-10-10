import time
import datetime
import threading

def getDate(day, month, year):
    try :
        d = datetime.date(int(year),int(month),int(day))
        return d
    except:
        return None
def getDateTime(day, month, year, hours = 0, minutes = 0, seconds = 0):
    try :
        d = datetime.datetime(int(year),int(month),int(day),int(hours), int(minutes), int(seconds))
        return d
    except:
        return None

#-1: Date in the past (date still valid)
# 0: OK
# 1: Invalid date
# 2: Parsing error
# 4: Invalid day in week
def parseDateTime(date, time):
    parsed_time = parseTime(time)
    if parsed_time == None:
        return (10, None, None)

    d = date.split('/')
    try:
        a = -1
        b = -1
        c = -1
        if len(d) >= 1:
            week_days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
            d[0] = d[0].lower()
            if d[0] in week_days:
                d[0] = week_days.index(d[0])
            a = int(d[0])
        if len(d) >= 2:
            b = int(d[1])
        if len(d) >= 3:
            c = int(d[2])
        if len(d) == 1:
            if a >= 0 and a <= 8:
                return (0, (a, -1, -1), parsed_time)
            else:
                return (4, None, None)
        if len(d) == 2:
            if getDate(a, b, 2000) != None:
                return (0, (a, b, -1), parsed_time)
            else:
                return (1, None, None)
        if len(d) == 3:
            # Because i dont know how to name these variables:
            fuck = getDateTime(a, b, c, parsed_time.hour, parsed_time.minute, parsed_time.second)
            you = datetime.datetime.now()
            if fuck != None:
                if fuck < you:
                    return (-1, (a, b, c), parsed_time)
                else:
                    return (0, (a, b, c), parsed_time)
            else:
                return (1, None, None)
    except Exception as e:
        print(e)
        return (2, None, None)
    return (2, None, None)

# 0: OK
# 1: Parsing error
# 2: Invalid time
def parseTime(time):
    t = time
    t = t.replace('h', ':')
    t = t.replace('m', '')
    t = t.replace('n', '')
    t = t.split(':')
    t+=[0]*(3-len(t))
    try :
        t = datetime.time(int(t[0]), int(t[1]), int(t[2]))
        return t
    except Exception as e:
        print(e)
        return None

# 00-10: Date error
# 10-20: Time error
# 20-30: Text error
def addEvent(data, date, time, text):
    (error_code, targetDate, targetTime) = parseDateTime(date, time)
    if error_code != 0:
        return (error_code, None, data)
    data = data + date + ',,' + time + ',,' + text + '\n'
    (targetDay, targetMonth, targetYear) = targetDate
    return (0, getNextTrig(datetime.datetime.today(), targetDay, targetMonth, targetYear, targetTime), data)

def getNextTrigBysextil(todayYear, targetDay, targetMonth, targetYear, targetTime):
    r = None
    try :
        r = datetime.datetime((todayYear&0xFFFC) + 4, targetMonth, targetDay, targetTime.hour, targetTime.minute, targetTime.second)
    except:
        # Beacause bysextil years can occurs after 8 years, instead of 4
        try :
            r = datetime.datetime((todayYear&0xFFFC) + 8, targetMonth, targetDay, targetTime.hour, targetTime.minute, targetTime.second)
        except:
            r = None # There is an error somewhere
    return r

def getNextTrig(today, targetDay, targetMonth, targetYear, targetTime):
    if targetMonth == -1 and targetYear == -1:
        delta = (targetDay+7-today.weekday())%7
        if delta == 0 and targetTime < today.time():
            delta = 7
        r = today
        r = r.replace(hour=targetTime.hour, minute=targetTime.minute, second=targetTime.second, microsecond=targetTime.microsecond)
        r = r + datetime.timedelta(days=delta)
        return r
    if targetYear == -1:
        r = None
        try :
            r = datetime.datetime(today.year, targetMonth, targetDay, targetTime.hour, targetTime.minute, targetTime.second)
        except:
            r = None
        if r == None: # looking for bysextil year or error
            return getNextTrigBysextil(today.year, targetDay, targetMonth, targetYear, targetTime)
        elif r > today:
            return r
        else:
            try :
                return datetime.datetime(today.year+1, targetMonth, targetDay, targetTime.hour, targetTime.minute, targetTime.second)
            except:
                return getNextTrigBysextil(today.year, targetDay, targetMonth, targetYear, targetTime)
    r = datetime.datetime(targetYear, targetMonth, targetDay, targetTime.hour, targetTime.minute, targetTime.second)
    if r > today:
        return r
    else:
        return None

def standardKeepFun(today, targetDay, targetMonth, targetYear, targetTime):
    dt = getNextTrig(today, targetDay, targetMonth, targetYear, targetTime)
    if dt == None:
        return (-1, None)
    delta_s = (dt-today).total_seconds()
    if delta_s < 3600*24:
        return (1, dt)
    else:
        return (0, dt)

def keepFunAll(today, targetDay, targetMonth, targetYear, targetTime):
    return (1, getNextTrig(today, targetDay, targetMonth, targetYear, targetTime))

def getEventList2(data, conv):
    return getEventList(data, conv, keepFunAll)

def getEventList(data, conv, keepFun=standardKeepFun):
    today = datetime.datetime.today()
    r = []
    newData = ""
    for l in data.split('\n'):
        m = l.split(',,')
        if len(m) == 3:
            (error_code, targetDate, targetTime) = parseDateTime(m[0], m[1])
            if error_code == 0:
                (targetDay, targetMonth, targetYear) = targetDate
                (kr, kdt) = keepFun(today, targetDay, targetMonth, targetYear, targetTime)
                if kr != -1:
                    newData+=l+'\n'
                if kr == 1:
                    r+=[(kdt, conv, m[2])]
    return (newData, r)

def defaultActionFun(ev_conv, ev_txt):
    print(ev_conv, ev_txt)

def eventThread(e, eventList, actionFun=defaultActionFun):
    eventList.sort()
    while True:
        today = datetime.datetime.today()
        if len(eventList) == 0:
            print("Event list terminated")
            return
        (ev_dt, ev_conv, ev_txt) = eventList[0]
        delta_s = (ev_dt-today).total_seconds()
        if delta_s < 1:
            del eventList[0]
            actionFun(ev_conv, ev_txt)
        elif delta_s < 60:
            if e.wait(timeout=delta_s):
                print("Event list terminated")
                return
        else:
            if e.wait(timeout=delta_s-60):
                print("Event list terminated")
                return

def startEventThread(eventList, actionFun = defaultActionFun):
    global threadingEvent
    threadingEvent = threading.Event()
    threading.Thread(target=eventThread, args=(threadingEvent, eventList, actionFun)).start()

def stopEventThread():
    try:
        global threadingEvent
        threadingEvent.set()
        return True
    except:
        return False
