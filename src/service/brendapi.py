import socket
import _thread

class Brendapi:
    callbackOnText = None
    callbackOnPermission = None
    common_socket = None
    started = False
    port = 65432
    ip_white_list = []

    def __init__(self, port, callbackOnText=lambda a,b,c,d:None, callbackOnPermission=lambda a,b,c,d:None):
        self.callbackOnText = callbackOnText
        self.callbackOnPermission = callbackOnPermission
        self.started = False
        self.port = port

    def updateIPWhiteList(self, file):
        f = open(file, "r")
        self.ip_white_list = f.read().split('\n')
        f.close()

    def _process_packet(self, data, clientsocket, addr):
        self.callbackOnText("".join([chr(i) for i in data]), self, clientsocket, addr)

    def _build_packet(self, l):
        s_u = len(l)>>8
        s_l = len(l)&0xFF
        return bytes([3, s_u, s_l]+l+[s_l])
    def _build_packet_text(self, text):
        return self._build_packet([ord(i) for i in text])
    def send_data(self, data, clientsocket=None):
        if clientsocket==None:
            clientsocket = self.common_socket
        try:
            clientsocket.send(data)
            return True
        except:
            return False
    def send_text(self, text, clientsocket=None):
        if clientsocket==None:
            clientsocket = self.common_socket
        return self.send_data(self._build_packet_text(text), clientsocket)

    def _process_client(self, clientsocket, addr):
        if len(self.ip_white_list) > 0:
            (ip_a, _) = addr
            if self.callbackOnPermission!=None and not(ip_a in self.ip_white_list):
                clientsocket.close()
                self.callbackOnPermission(ip_a)
                return
        header_size = -1
        data_size = -1
        pointer = -1
        data = []
        while True:
            msg = clientsocket.recv(1024)
            if len(msg) == 0:
                break
            for i in msg:
                v = int(i)
                if header_size == -1:
                    header_size = v
                    pointer = 0
                    data_size = 0
                    data = []
                else:
                    pointer+=1
                    if pointer==header_size-2 or pointer==header_size-1:
                        data_size = (data_size<<8) | v
                    elif pointer == header_size+data_size:
                        if data_size&0xFF != v:
                            print("Bad packet received")
                            break
                        else:
                            self._process_packet(data, clientsocket, addr)
                            header_size = -1
                    else:
                        data+=[v]
        clientsocket.close()

    def _run(self):
        self.common_socket = socket.socket()
        self.common_socket.bind(('0.0.0.0', self.port))
        self.common_socket.listen(5)
        self.started = True
        while True:
            c, addr = self.common_socket.accept()
            if self.started:
                _thread.start_new_thread(self._process_client, (c, addr))
            else:
                break
        self.common_socket.close()

    def start(self):
        _thread.start_new_thread(self._run, ())
    def stop(self):
        if self.started:
            self.started = False
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', self.port))
            s.close()


    # Functions on client side
    def receiveText(self):
        try:
            header_size = -1
            data_size = -1
            pointer = -1
            data = []
            while True:
                self.common_socket.settimeout(5.0)
                msg = self.common_socket.recv(1024)
                if len(msg) == 0:
                    return ""
                for i in msg:
                    v = int(i)
                    if header_size == -1:
                        header_size = v
                        pointer = 0
                        data_size = 0
                        data = []
                    else:
                        pointer+=1
                        if pointer==header_size-2 or pointer==header_size-1:
                            data_size = (data_size<<8) | v
                        elif pointer == header_size+data_size:
                            if data_size&0xFF != v:
                                print("Bad packet received")
                                return ""
                            else:
                                header_size = -1
                                return data
                        else:
                            data+=[v]
            return ""
        except:
            print("Timeout")
            return ""
    def connect(self):
        try:
            self.common_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.common_socket.connect(('127.0.0.1', self.port))
            return True
        except:
            return False
    def disconnect(self):
        self.common_socket.close()


#Example

#import time
#def brendapiCallbackOnText(text, brendapi, clientsocket, addr):
#    print("Received text:", text)
#    brendapi.send_text("Response", clientsocket)
#def brendapiCallbackOnPermission(ip_a):
#    print("IP not allowed:", ip_a)

#brendapi = Brendapi(65432, brendapiCallbackOnText, brendapiCallbackOnPermission)
#brendapi.start()
#while True:
#    print("Timer")
#    time.sleep(20)
