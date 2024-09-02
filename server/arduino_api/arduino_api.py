import json
import serial
import serial.tools.list_ports
import time

data_table = dict()

class Motor(object):
    angle = None
    def __init__(self, code):
        self.angle = 0
        self.code = code
        data_table[code] = self.angle
    def get(self):
        self.angle = data_table[self.code]
        return self.angle
    def set(self, angle):
        self.angle = angle
        commander("svo", self.code, "s", angle)
        return self.angle

class Engine(object):
    speed = None
    def __init__(self, code):
        self.speed = 0
        self.code = code
        data_table[code] = self.speed
    def get(self):
        self.speed = data_table[self.code]
        return self.speed
    def tune(self, new_speed):
        self.speed = new_speed
        commander("eng", self.code, "s", new_speed)
        return self.speed

class Battery:
    def get():
        power_left = 0.9
        return power_left
    def stat():
        status = "Unplugged"
        return status

class Serial:
    ino = serial.Serial("COM7", 9600, timeout=2)
    if ino.is_open:
        print("串口初始化成功")
    def close():
        Serial.ino.close()
    def write(data):
        n = Serial.ino.write(data.encode())
        print(f"写入 {n} 字节", data.encode())
    def readln():
        data = Serial.ino.readline()
        print(f"读入: {data.decode('utf-8', 'ignore')}\n")
        return data.decode('utf-8', 'ignore')

def commander(type, device, option, num = -1):
    d = f""""type":"{type}", "device":"{device}", "option":"{option}", "num":{num}"""
    d = "{" + d + "}"
    Serial.write(d)
    if option == "q":
        b = Serial.readln()
        if b.strip() != "":
            print("BIS", b)
            b = json.loads(b)
            for i in b.keys():
                data_table[i] = b[i]

def debug():
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("无串口设备。")
    else:
        print("可用的串口设备如下：")
        for comport in ports_list:
            print(list(comport)[0], list(comport)[1])
    #Serial.init()
    #time.sleep(1)
    #print("hi",a)
    #Serial.readln()
    Serial.close()
    """/*
        data["t(ype)"]: svo/eng
        data["d(evice)"]: al, ar, tl, tr
        data["o(ption)"]: s(et)/q(uery)
        data["n(um)"]: SHORT
    */"""

if __name__ == "__main__":
    debug()