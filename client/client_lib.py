import socket
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Net(object):
    data = None
    jdata = None
    name = None
    isfirst = 0

    def __init__(self, dest="127.0.0.1", port=40808):
        logging.info("Start remote host communcation")
        self.dest = dest
        self.port = port
        self.remote = socket.socket()
        self.remote.connect((dest, port))
        self.data: str = self.remote.recv(2048).decode("UTF-8")
        self.jdata = json.loads(self.data)
        first = json.loads(self.data)
        self.name = first["name"]
        logging.info(f"Connected to {self.name}")
        self.isfirst = 1

    def send(self, msg):
        size = len(msg.encode())
        self.remote.send(msg.encode("UTF-8").ljust(2048 - size))
        self.jdata = json.loads(self.data)

    def recv(self):
        self.data: str = self.remote.recv(2048).decode("UTF-8")
        self.jdata = json.loads(self.data)
        return self.data

    def jsend(self, msg):
        msg = json.dumps(msg)  # 状态回传
        size = len(msg.encode())
        self.remote.send(msg.encode("UTF-8").ljust(2048 - size))
        self.jdata = json.loads(self.data)
        print("发送",msg)

    def refresh(self):
        if self.isfirst == 1:
            self.isfirst = 0
            return self.jdata
        self.data: str = self.remote.recv(2048).decode("UTF-8")
        self.jdata = json.loads(self.data.encode("UTF-8"))
        return
