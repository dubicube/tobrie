import socket
import _thread

class RemoteServiceServer:
    started = False
    port = 65332
    clients = []

    def __init__(self, port):
        self.started = False
        self.port = port
        self.clients = []

    def sendToClient(self, data):
        if not self.isClientConnected() or len(data) == 0:
            return ""
        if data[-1] != '\n':
            data+='\n'
        response = ""
        listening = True
        try:
            self.clients[0].send(bytes(data, 'utf-8'))
            while listening:
                msg = str(self.clients[0].recv(1024).decode('utf-8'))
                if len(msg) == 0 or '\n' in msg:
                    listening = False
                response+=msg
            return response
        except:
            return ""

    def isClientConnected(self):
        return len(self.clients) > 0

    def _run(self):
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(5)
        self.started = True
        while True:
            c, addr = server_socket.accept()
            if self.started:
                c.settimeout(10)
                self.clients = [c]
            else:
                break
        if len(self.clients) > 0:
            self.clients.close()
        server_socket.close()

    def start(self):
        _thread.start_new_thread(self._run, ())
    def stop(self):
        if self.started:
            self.started = False
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', self.port))
            s.close()


# import time
# r = RemoteServiceServer(65332)
# r.start()
# time.sleep(3)
# print("Response:", r.sendToClient("heure"))
# time.sleep(20)
# r.stop()
