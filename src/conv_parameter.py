import data_manager
from config import *

class ConvParameter:
    def __init__(self, conv):
        self.conv_id = conv
        ConvParameter.dmanager = data_manager.DataManager(conv_config_path)
        raw_data = ConvParameter.dmanager.getRessource(self.conv_id, 'config')
        if raw_data == "":
            self.data = {}
            self.data["AUTOREPLY_ENABLE"] = "True"
            self.data["TEXT_ENABLE"] = "True"
            self.data["STICKER_ENABLE"] = "True"
            self.data["VIDEO_ENABLE"] = "True"
            self.data["PROBAS"] = "100,100,100,100,100"
            self.__save()
        else:
            self.data = {}
            for i in raw_data.split('\n'):
                l = i.split('£')
                if len(l) == 2:
                    self.data[l[0]] = l[1]
    def __save(self):
        raw_data = ''
        for key,value in self.data.items():
            raw_data+=key+'£'+value+'\n'
        ConvParameter.dmanager.saveRessource(self.conv_id, 'config', raw_data)
    def getBoolean(self, key):
        d = self.data.get(key, False)
        if d == 'True':
            return True
        if d == 'False':
            return False
        return False
    def setBoolean(self, key, value):
        self.data[key] = str(value==True or value=='1' or str(value).lower()=='true')
        self.__save()

    def getList(self, key):
        return self.data.get(key, "").split(',')
    def setList(self, key, value):
        self.data[key] = ','.join([str(i) for i in value])
        self.__save()

class ConvParameterList:
    def __init__(self):
        self.conv_parameters = {}
    def getConv(self, conv):
        conv = str(conv)
        if not conv in self.conv_parameters:
            self.conv_parameters[conv] = ConvParameter(conv)
        return self.conv_parameters[conv]
