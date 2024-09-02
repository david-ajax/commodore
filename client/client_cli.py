import socket
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def operate():
    strs = input()
    return strs

dest = "127.0.0.1"
port = 40808

logging.info("启动 AZURE 客户端")
logging.info("启动远程主机网络通讯")
remote = socket.socket()
remote.connect((dest, port))

data: str = remote.recv(2048).decode("UTF-8")
first = json.loads(data)
devices = first["devices"]
name = first["name"]
logging.info(f"已链接至 {name}")

while True:
    msg = json.dumps(operate())  # 状态回传
    size = len(msg.encode())
    remote.send(msg.encode("UTF-8").ljust(2048 - size))  # encode将字符串编码为字节数组对象
    logging.info("命令已回传")
