import dummy_api as ctrl
import time
import os
import threading
class Flank(object):
    motor = None
    name = None
    curr_angle = None
    id = None
    type = "flank"
    def __init__(self, name, id):
        self.motor = ctrl.Motor(id)
        self.curr_angle = self.motor.get()
        self.name = name
        self.id = id
        print("初始化操纵面 {}, 硬件代号绑定为 {}".format(name, id))
    def add_angle(self, angle):
        self.motor.turn(angle)
        self.curr_angle = self.motor.get();
        #print("将 {} 的角度加成 {} 度".format(self.name, angle))
    def set_angle(self, angle):
        angle_turn = angle - self.motor.get()
        self.motor.turn(angle_turn)
        self.curr_angle = self.motor.get()
        #print("将 {} 的角度设置为 {} 度".format(self.name, angle))
    def get_angle(self):
        self.curr_angle = self.motor.get()
        #print("{} 当前角度为 {} 度".format(self.name, self.curr_angle))
        return self.curr_angle
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
    id = None
    name = None
    type = "engine"
    def __init__(self, name, id):
        self.id = id
        self.name = name
        self.engine = ctrl.Engine(id)
        self.curr_speed = self.engine.get()
        print("初始化引擎 {}, 硬件代号绑定为 {}".format(name, id))
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

class Sensor:
    data = dict()
    data["speed"] = 0
    data["battery"] = 0
    data["xangle"] = 0
    data["yangle"] = 0
    data["zangle"] = 0
    data["sign"] = 0
    data["cpuload"] = 0
    data["memload"] = 0
    data["memsum"] = 0
    data["torch"] = 0
    data["acc"] = 0
    is_torch_on = 0

    @staticmethod
    def speed():
        Sensor.data["speed"] = 99
        return Sensor.data["speed"]

    @staticmethod
    def battery():
        Sensor.data["battery"] = 0.8
        return Sensor.data["battery"]

    @staticmethod
    def xangle():
        Sensor.data["xangle"] = 201
        return Sensor.data["xangle"]

    @staticmethod
    def yangle():
        Sensor.data["yangle"] = 108
        return Sensor.data["yangle"]

    @staticmethod
    def zangle():
        Sensor.data["zangle"] = 0
        return Sensor.data["zangle"]

    @staticmethod
    def sign():
        Sensor.data["sign"] = 322
        return Sensor.data["sign"]

    @staticmethod
    def cpuload():
        Sensor.data["cpuload"] = 0.12
        return Sensor.data["cpuload"]

    @staticmethod
    def memload():
        Sensor.data["memload"] = 0.88
        return Sensor.data["memload"]

    @staticmethod
    def memsum():
        Sensor.data["memsum"] = 2048
        return Sensor.data["memsum"]

    @staticmethod
    def torch():
        Sensor.data["torch"] = Sensor.is_torch_on
        return Sensor.data["torch"]

    @staticmethod
    def torchon():
        Sensor.is_torch_on = 1

    @staticmethod
    def acc():
        Sensor.data["acc"] = 3
        return Sensor.data["acc"]

    @staticmethod
    def net_delay():
        Sensor.data["net_delay"] = 300
        return Sensor.data["net_delay"]
    
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
        Sensor.acc()
        Sensor.net_delay()
    
    @staticmethod
    def stat():
        #Sensor.refresh()
        return Sensor.data

    def pseudo_gui():
        import tkinter as tk
        def update_label(key, value):
            labels[key].config(text=f"{key}: {value}")
        def update():
            while 1:
                for key in Sensor.data.keys():
                    Sensor.data[key] = sliders[key].get()
        root = tk.Tk()
        root.title("DEBUGGING CONSOLE")

        labels = {}
        sliders = {}

        # 自动布局
        for key in Sensor.data.keys():
            # 创建标签
            label = tk.Label(root, text=f"{key}: {Sensor.data[key]}")
            label.pack()
            labels[key] = label

            # 创建滑块
            slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=lambda value, k=key: update_label(k, value))
            slider.pack()
            sliders[key] = slider
        
        up = threading.Thread(target=update, name='Update')
        up.start()
        root.mainloop()
        up.join()
