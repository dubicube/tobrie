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
