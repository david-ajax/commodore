class Motor(object):
    angle = None
    def __init__(self, id):
        self.angle = 0 # mark
        self.id = id
    def get(self):
        return self.angle
    def turn(self, add_angle):
        self.angle += add_angle
        return self.angle
class Engine(object):
    speed = None
    def __init__(self, id):
        self.speed = 0 # Mark
        self.id = id
    def get(self):
        return self.speed
    def tune(self, new_speed):
        self.speed = new_speed
        return self.speed

class Battery:
    def get():
        power_left = 0.9
        return power_left
    def stat():
        status = "Unplugged"
        return status
    
class Network:
    def stat():
        delay = 0.2 # ms
        return delay # or -1 (unreachable)