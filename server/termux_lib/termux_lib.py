import sys
import os
sys.path.append("../arduino_api")
import arduino_api as ctrl
import time
import os
import threading
import json
import subprocess
import psutil
import threading

class Flank(object):
    motor = None
    name = None
    curr_angle = None
    code = None
    type = "flank"
    def __init__(self, name, code):
        self.motor = ctrl.Motor(code)
        self.curr_angle = self.motor.get()
        self.name = name
        self.code = code
        print("初始化操纵面 {}, 硬件代号绑定为 {}".format(name, code))
    def set_angle(self, angle):
        self.motor.set(angle)
        self.curr_angle = self.motor.get()
        #print("将 {} 的角度设置为 {} 度".format(self.name, angle))
    def add_angle(self, add_angle):
        self.motor.set(self.curr_angle + add_angle)
        self.curr_angle = self.motor.get()
    def status(self):
        return {"type":"Flank", "name":self.name, "angle":self.curr_angle}
    def selfchk(self):
        print("开始自检操纵面 {}".format(self.name))
        self.add_angle(30)
        self.add_angle(-60)
        self.set_angle(0)

class Engine(object):
    engine = None
    curr_speed = None
    code = None
    name = None
    type = "engine"
    def __init__(self, name, code):
        self.code = code
        self.name = name
        self.engine = ctrl.Engine(code)
        self.curr_speed = self.engine.get()
        print("初始化引擎 {}, 硬件代号绑定为 {}".format(name, code))
    def set_speed(self, new_speed):
        self.engine.tune(new_speed)
        self.curr_speed = self.engine.get()
        ##print("将 {} 的转速调谐为 {} RPM".format(self.name, new_speed))
    def add_speed(self, add_speed):
        self.engine.tune(self.curr_speed + add_speed)
        self.curr_speed = self.engine.get()
        ##print("将 {} 的转速加成 {} RPM".format(self.name, add_speed))
    def get_speed(self):
        ##print("{} 当前转速为 {} RPM".format(self.name, self.curr_speed))
        self.curr_speed = self.engine.get()
        return self.curr_speed
    def status(self):
        ##print(self.curr_speed)
        return {"type":"Engine", "name":self.name, "speed":self.get_speed()}
    def selfchk(self):
        print("开始自检引擎 {}".format(self.name))
        self.add_speed(3)
        self.add_speed(-6)
        self.set_speed(0)
        self.curr_speed = self.engine.get()


"""
@liteon-proximity: 光学接近传感器,用于检测物体的接近
!yas537-mag: 磁力计传感器,用于测量磁场强度和方向
@liteon-light: 光传感器,用于测量环境光强度
@MPU6050-gyro: 陀螺仪传感器,用于测量角速度
@MPU6050-accel: 加速度计传感器,用于测量线性加速度
!liteon-pocket: 可能是特定用途的传感器,具体功能需参考设备文档
*yas537-orientation: 方向传感器,结合磁力计和加速度计数据来确定设备的方向
@Game Rotation Vector Sensor: 用于测量设备的旋转向量,常用于游戏和增强现实应用
@GeoMag Rotation Vector Sensor: 结合地磁和加速度数据来测量设备的旋转向量
@Gravity Sensor: 测量重力加速度,用于确定设备的姿态
*Linear Acceleration Sensor: 测量去除重力影响后的线性加速度
@Rotation Vector Sensor: 综合陀螺仪和加速度计数据来测量设备的旋转向量
"""

class Sensor:
    data = {
        "speed": 0,
        "battery": 0,
        "xangle": 0,
        "yangle": 0,
        "zangle": 0,
        "sign": 0,
        "cpuload": 0,
        "memload": 0,
        "memsum": 0,
        "torch": 0,
        "acc": 0
    }
    is_torch_on = 0
    @staticmethod
    def speed(): #TODO
        Sensor.data["speed"] = -1
        return Sensor.data["speed"]

    @staticmethod
    def battery(): # 电池剩余
        return Sensor.data["sysbattery"]
    
    def battery(): # TODO: 电机电池剩余
        return Sensor.data["battery"]

    @staticmethod
    def xangle(): # X迎角
        return Sensor.data["xangle"]

    @staticmethod
    def yangle():
        return Sensor.data["yangle"]

    @staticmethod
    def zangle():
        return Sensor.data["zangle"]

    @staticmethod
    def sign(): # 信号强度
        Sensor.data["sign"] = -1
        return Sensor.data["sign"]

    @staticmethod
    def cpuload(): # CPU占用(百分比)
        Sensor.data["cpuload"] = psutil.cpu_percent(interval=1) / 100
        return Sensor.data["cpuload"]

    @staticmethod
    def memload(): # 内存占用(百分比)
        Sensor.data["memload"] = psutil.virtual_memory().percent / 100
        return Sensor.data["memload"]

    @staticmethod
    def memsum(): # 内存总量(MB)
        return Sensor.data["memsum"]

    @staticmethod
    def torch():
        return Sensor.data["torch"]

    @staticmethod
    def torchon(): # 打开电筒
        Sensor.is_torch_on = not Sensor.is_torch_on
        to = {0:"off", 1:"on"}
        os.system(f"torch {to[Sensor.is_torch_on]} &")

    @staticmethod
    def refresh():
        Sensor.speed()
        Sensor.battery()
        Sensor.xangle()
        Sensor.yangle()
        Sensor.zangle()
        Sensor.sign()
        Sensor.cpuload()
        Sensor.memload()
        Sensor.memsum()
        Sensor.torch()
    
    @staticmethod
    def stat():
        #Sensor.refresh()
        return Sensor.data

    def update_battery():
        while True:
            result = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
            data = json.loads(result.stdout)
            Sensor.data["sysbattery"] = data["percentage"]

    def update_orientation():
        while True:
            # TODO: 优化
            result = subprocess.run(['termux-sensor', '-s', 'yas537-orientation', '-n', '1'], capture_output=True, text=True)
            data = json.loads(result.stdout)
            Sensor.data["xangle"] = data["yas537-orientation"]["values"][0]
            Sensor.data["yangle"] = data["yas537-orientation"]["values"][1]
            Sensor.data["zangle"] = data["yas537-orientation"]["values"][2]

    def update_acceleration():
        while True:
            result = subprocess.run(['termux-sensor', '-s', 'Linear Acceleration Sensor', '-n', '1'], capture_output=True, text=True)
            data = json.loads(result.stdout)
            Sensor.data["acc"] = data["Linear Acceleration Sensor"]["values"]
    
    def update_func(cmd):
        while True:
            exec(cmd)
            time.sleep(0.1)
    def init():
        Sensor.data = {
            "speed": 0,
            "battery": 0,
            "xangle": 0,
            "yangle": 0,
            "zangle": 0,
            "sign": 0,
            "cpuload": 0,
            "memload": 0,
            "memsum": 0,
            "torch": 0,
            "acc": 0
        }
        os.system("termux-torch off &")
        Sensor.is_torch_on = 0
        Sensor.data["memsum"] = psutil.virtual_memory().total / (1024 * 1024)

    def deamon():
        # 启动线程
        Sensor.battery_thread = threading.Thread(target=Sensor.update_battery)
        Sensor.orientation_thread = threading.Thread(target=Sensor.update_orientation)
        Sensor.acceleration_thread = threading.Thread(target=Sensor.update_acceleration)
        Sensor.other_thread = threading.Thread(target=Sensor.update_func, args=("""Sensor.sign()\nSensor.cpuload()\nSensor.memload()\nSensor.torch()"""))
        Sensor.battery_thread.start()
        Sensor.orientation_thread.start()
        Sensor.acceleration_thread.start()
    def stop():
        Sensor.orientation_thread.join()
        Sensor.battery_thread.join()
        Sensor.acceleration_thread.join()
        Sensor.other_thread.join()
