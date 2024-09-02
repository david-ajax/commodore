__dummy_mode__ = 1

if not __dummy_mode__:
    import sys, os
    sys.path.append("arduino_api")
    sys.path.append("termux_lib")
    import termux_lib as lib
    import socket
    import json
    import os
    import time
    import threading
else:
    import sys
    sys.path.append("dummy_all")
    import dummy_lib as lib
    import socket
    import json
    import os
    import time
    import threading

name = "零号侧卫"
global hw
hw = dict()
def hwinit():
    global hw
    hw = dict()
    hw["aile_left"] = lib.Flank("左副翼", "al")
    hw["aile_right"] = lib.Flank("右副翼", "ar")
    #hw["tail_vert"] = lib.Flank("垂直尾翼", "tv")
    hw["tail_left"] = lib.Flank("左尾翼", "tl")
    hw["tail_right"] = lib.Flank("右尾翼", "tr")
    hw["engine_main"] = lib.Engine("一号引擎", "e1")
    

def check():
    for i in hw.values():
        i.selfchk()
    print("操纵面与引擎自检完成, 等待远程指令")

def proc(data):
    global hw
    #print(data)
    inf = json.loads(data.replace('\n', ';'))
    print("DT"+data + "DT")
    if inf["type"] == "cmd":
        #print(f"执行命令")
        exec(inf["cmd"])
    elif inf["type"] == "syscmd":
        #print(f"执行系统级命令")
        os.system(inf["cmd"])
    elif inf["type"] == "reset":
        pass
        #print(f"系统重置")
    elif inf["type"] == "stop":
        #print(f"退出系统")
        return 1
    else:
        pass
        #print(f"未知命令")
    return 0
global isx
isx = 0
def stat():
    global isx
    status = dict()
    status["devices"] = dict()
    for i in hw.items():
        status["devices"][i[0]] = i[1].status()
    status["name"] = name
    status["sensors"] = lib.Sensor.stat()
    status["time"] = time.asctime()
    isx+=1
    return status
def debug_shell():
    lib.Sensor.pseudo_gui()
port = 40808
password = "thepassword"

print(f"启动 {name} 服务端")
print(f"硬件初始化")
print 
hwinit()
print("开始操纵面与引擎自检")
check()

print(f"启动 {name} 的主机网络通讯")
dummy = socket.socket()
dummy.bind(("localhost", port)) # 端口监听
dummy.listen(1)
print(f"监听端口 " + str(port))
conn, address = dummy.accept()
print(f"来自 {address} 的连接已接收")
 
msg = json.dumps(stat()) # 状态回传
size = len(msg.encode())
conn.send(msg.encode("UTF-8").ljust(2048))

np = threading.Thread(target=debug_shell, name='Debugging')
np.start()
while True:
    # 接收消息
    print(lib.Sensor.data)
    data: str = conn.recv(2048).decode("UTF-8")
    if data == "" or data == None:
        continue
    print(f"命令接收: {data}")
    ret = proc(data)
    if ret == 1:
        break
    msg = json.dumps(stat()) # 状态回传
    size = len(msg.encode())
    conn.send(msg.encode("UTF-8").ljust(2048 - size))  # encode将字符串编码为字节数组对象
    #print(msg.encode("UTF-8").decode('unicode_escape'))
    #print(f"当前状态已回传")

# 关闭连接
conn.close()
dummy.close()
np.join()