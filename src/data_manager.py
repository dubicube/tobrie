import os

class DataManager:
    def __init__(self, path='../data/'):
        self.dataPath = path
        if not os.path.exists(self.dataPath):
            os.mkdir(self.dataPath)
    def __createSpace(self, conv):
        os.mkdir(self.dataPath+conv)
    def __checkSpace(self, conv, name):
        if not os.path.exists(self.dataPath+conv):
            self.__createSpace(conv)
        if not os.path.exists(self.dataPath+conv+name):
            f = open(self.dataPath+conv+name, "w")
            f.close()

    def getRessource(self, conv, name):
        conv = str(conv)+'/'
        self.__checkSpace(conv, name)
        f = open(self.dataPath+conv+name, "r")
        data = f.read()
        f.close()
        return data
    def saveRessource(self, conv, name, data, mode="w"):
        conv = str(conv)+'/'
        self.__checkSpace(conv, name)
        f = open(self.dataPath+conv+name, mode)
        f.write(data)
        f.close()


    # When using "smart" methods:
    # This allows to store multiple lines of information in 1 file.
    # Each line of the file contains a key, and a data.
    # Thus, the data cannot contains in line return, and in fact,
    # any line return will be automatically removed whenn calling saveRessourceSmart().
    # Typically, these methods allows to store a specific information for each user of a chat in a single file.
    def getRessourceSmart(self, conv, name, key):
        conv = str(conv)+'/'
        self.__checkSpace(conv, name)
        f = open(self.dataPath+conv+name, "r")
        data = f.read().split('\n')
        f.close()
        for line in data:
            if line.startswith(key) and len(line) > len(key)+1:
                return line[len(key)+1:]
        return ""
    def saveRessourceSmart(self, conv, name, key, data):
        conv = str(conv)+'/'
        self.__checkSpace(conv, name)
        f = open(self.dataPath+conv+name, "r")
        filedata = f.read().split('\n')
        f.close()
        data_is_written = False
        i = 0
        while i < len(filedata):
            if filedata[i].startswith(key):
                if not data_is_written:
                    filedata[i] = key + " " + data
                    data_is_written = True
                else:
                    # Delete duplicate
                    del (data[i])
                    i-=1
            i+=1
        if not data_is_written:
            # Create line
            filedata += [key + " " + data]
        f = open(self.dataPath+conv+name, 'w')
        f.write('\n'.join(filedata))
        f.close()

    # Returns all the currently known conv IDs
    def getConvNames(self):
        directories = []
        dir = os.scandir(self.dataPath)
        for entry in dir:
            if not entry.is_file():
                directories+=[entry.name+"/"]
        directories = sorted(directories)
        return directories


# Example
# dm = DataManager()
# dm.saveRessource(42, "id", "Bonjour\nOui")
# print(dm.getRessource("42", "id"))
# print(dm.getRessource("aze", "kjfd"))
# print(dm.getRessource("zfe", "id"))
