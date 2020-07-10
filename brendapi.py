import socket
import _thread

class Brendapi:
    callbackOnText = None
    common_socket = None
    started = False

    def __init__(self, c):
        self.callbackOnText = c
        self.started = False

    def _process_packet(self, data, clientsocket, addr):
        self.callbackOnText("".join([chr(i) for i in data]), self, clientsocket, addr)

    def _build_packet(self, l):
        s_u = len(l)>>8
        s_l = len(l)&0xFF
        return bytes([3, s_u, s_l]+l+[s_l])
    def _build_packet_text(self, text):
        return self._build_packet([ord(i) for i in text])
    def send_data(self, data, clientsocket):
        clientsocket.send(data)
    def send_text(self, text, clientsocket):
        clientsocket.send(self._build_packet_text(text))

    def _process_client(self, clientsocket, addr):
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
                        if v&0xFF != data_size:
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
        self.common_socket.bind(('0.0.0.0', 65432))
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
            s.connect(('127.0.0.1', 65432))
            s.close()


#Example

#import time
#def brendapiCallbackOnText(text, brendapi, clientsocket, addr):
#    print("Received text:", text)
#    brendapi.send_text("Response", clientsocket)

#brendapi = Brendapi(brendapiCallbackOnText)
#brendapi.start()
#while True:
#    print("Timer")
#    time.sleep(20)
