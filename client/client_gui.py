from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame.locals import *
import cv2
import client_lib as lib
import math
import time
import threading
import logging

camera_enabled = 0

def camera_refresh():
    global frame_surface
    if camera_enabled:
        frame = camera.read()[1]
        frame_rgb = cv2.resize(cv2.flip(cv2.rotate(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), cv2.ROTATE_90_CLOCKWISE), 1), (height, width))
        frame_surface = pygame.surfarray.make_surface(frame_rgb)
    else:
        frame_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        frame_surface.fill((0, 0, 0, 250))  # 将表面填充为完全透明

def welcome():
    for i in range(0, 120):
        screen.fill("black")
        text = fonts['huge'].render("Initialize Azure Network BVLOS Flighting Controlling System", True, colors['main'], None)
        screen.blit(text, (width / 2 - text.get_width() / 2, height / 2 - 150))
        text = fonts['big'].render(f"Remote connection: {remote.name}", True, colors['main'], None)
        screen.blit(text, (width / 2 - text.get_width() / 2, height / 2))
        pygame.display.flip()
        clock.tick(60)
def cmdgen():
    global devices
    cmd = ""
    for i in devices.keys():
        word = ""
        if remote.jdata["devices"][i]['type'] == "Flank":
            word = "angle"
        if remote.jdata["devices"][i]['type'] == "Engine":
            word = "speed"
        cmd += f"hw['{i}'].set_{word}({devices[i]})\n"
    # loggin.info(cmd)
    return cmd
def transmit(type, cmd):
    msg = dict()
    msg['type'] = type
    msg['cmd'] = cmd
    msg['time'] = time.asctime()
    remote.jsend(msg)
def update():
    global remote_devices, sensors
    remote.refresh()
    types = {'Flank':'angle', 'Engine':'speed'}
    for i in devices.keys():
        remote_devices[i] = remote.jdata['devices'][i][types[remote.jdata['devices'][i]['type']]]
    for i in sensors.keys():
        sensors[i] = remote.jdata['sensors'][i]
def calc_pair2angle(dyna):
    tan = (dyna[0][1] - dyna[1][1]) / (dyna[0][0] - dyna[1][0])
    return round(math.degrees(math.atan(tan)), 1)
def calc_langle(posx):
    if (width / 2 - 30 < mousepos[0] < width / 2 + 30) and (height / 2 - 30 < mousepos[1] < height / 2 + 30):
        global f_shootmode
        f_shootmode = 1
        return 0
    f_shootmode = 0
    a = abs(posx - width / 2) / (width * 0.76) * lwidth # 底边
    b = vdist
    angle_a = math.atan(a / b)
    angle_a = math.degrees(angle_a)
    if posx < width / 2:
        angle_a = -angle_a
    return angle_a
def calc_vangle(posy):
    if (width / 2 - 30 < mousepos[0] < width / 2 + 30) and (height / 2 - 30 < mousepos[1] < height / 2 + 30):    
        global f_shootmode
        f_shootmode = 1
        return 0
    f_shootmode = 0
    a = abs(posy - height / 2) / (height * 0.5) * vwidth # 底边
    b = vdist
    angle_a = math.atan(a / b)
    angle_a = math.degrees(angle_a)
    if posy < height / 2:
        angle_a = -angle_a
    return angle_a
def calc_langle2(posx):
    a = abs(posx - width / 2) / (width * 0.76) * lwidth # 底边
    b = vdist
    angle_a = math.atan(a / b)
    angle_a = math.degrees(angle_a)
    if posx < width / 2:
        angle_a = -angle_a
    return angle_a
def calc_vangle2(posy):
    a = abs(posy - height / 2) / (height * 0.5) * vwidth # 底边
    b = vdist
    angle_a = math.atan(a / b)
    angle_a = math.degrees(angle_a)
    if posy < height / 2:
        angle_a = -angle_a
    return angle_a
def showtext(text, pos, color = 'main', fontid = "medium"):
    db_text = fonts[fontid].render(text, 0 if fontid == "tiny" else 1, colors[color], None)
    screen.blit(db_text, pos)
def showline(pos1, pos2, width = 2, color = 'main'):
    pygame.draw.line(screen, colors[color], pos1, pos2, width)
def debug_ui():
    global sensors
    showtext(f"远程方位角(Z): {sensors['zangle']}", (32, 844), fontid = "tiny")
    showtext(f"远程滚动角(Y): {sensors['yangle']}", (32, 858), fontid = "tiny")
    showtext(f"远程倾斜角(X): {sensors['xangle']}", (32, 872), fontid = "tiny")
    showtext(f"本地滚动角(Y): {langle}", (32, 886), fontid = "tiny")
    showtext(f"本地倾斜角(X): {vangle}", (32, 900), fontid = "tiny")
    showtext(f"远程主机时间戳: {remote.jdata['time']}", (32, 914), fontid = "tiny")
    showtext(f"航行灯状态: {'打开' if sensors['torch'] else '关闭'}", (32, 928), fontid = "tiny")
    showtext(f"瞬时加速度: {sensors['acc']}", (32, 942), fontid = "tiny")
    showtext(f"远程信号强度: {sensors['sign']}", (32, 956), fontid = "tiny")
    showtext(f"远程 CPU 负载: {sensors['cpuload'] * 100} %", (32, 970), fontid = "tiny")
    showtext(f"远程内存占用: {sensors['memload'] * 100} %", (32, 984), fontid = "tiny")
    showtext(f"武装: 无", (32, 998), fontid = "tiny")
    showtext(f"挂载: 无", (32, 1012), fontid = "tiny")
def warn_layer(text):
    if 3 < flamenum % 15 < 12:
        showtext(text, (width / 2 - fonts['huge'].render(text, True, colors['warn'], None).get_width() / 2, height / 2 - 150), color=colors['warn'], fontid="huge")
def text_layer():
    global sensors, remote_devices
    showtext(f"远程主机: {remote.name}", (0, 0))
    showtext(f"虚拟视距: {vdist}cm", (0, 24))
    showtext(f"水平指示器宽度: {lwidth}cm", (0, 48))
    showtext(f"竖直指示器宽度: {round(vwidth)}cm", (0, 72))
    oriword = {0: "[N]", 90: "[E]", 180: "[S]", 270: "[W]"}
    for i in range(0, 13):
        showtext(f'{str(oriword[n] if (n := round(abs(calc_langle2(width * 0.12 + width * 0.76 * i / 12) + sensors["zangle"]))) in oriword.keys() else n).zfill(2)}', 
                (width * 0.12 + width * 0.76 * i / 12 - 12, height * 0.1 + width * 0.01))

    for i in range(0, 9):
        showtext(f'{str(round(abs(calc_vangle2(height * 0.25 + height * 0.5 * i / 8) - sensors["yangle"]))).zfill(2)}', 
                (width * 0.926, height * 0.25 + height * 0.49 * i / 8 - 3), fontid="small")
        showtext(f'{str(round(abs(calc_vangle2(height * 0.25 + height * 0.5 * i / 8) - sensors["yangle"]))).zfill(2)}', 
                (width * 0.064, height * 0.25 + height * 0.49 * i / 8 - 3), fontid="small")

    showtext("右副翼 >", (width * 0.95, height * 0.81), fontid="tiny")
    showtext(f"{devices['aile_right']}/{round(remote_devices['aile_right'], 1)}", (width * 0.955, height * 0.825), fontid="tiny")
    showtext("右尾翼 >", (width * 0.95, height * 0.93), fontid="tiny")
    showtext(f"{devices['tail_right']}/{round(remote_devices['tail_right'], 1)}", (width * 0.955, height * 0.915), fontid="tiny")
    showtext("左副翼 >", (width * 0.92, height * 0.81), fontid="tiny")
    showtext(f"{devices['aile_left']}/{round(remote_devices['aile_left'], 1)}", (width * 0.925, height * 0.825), fontid="tiny")
    showtext("左尾翼 >", (width * 0.92, height * 0.93), fontid="tiny")
    showtext(f"{devices['tail_left']}/{round(remote_devices['tail_left'], 1)}", (width * 0.925, height * 0.915), fontid="tiny")
    showtext("转速", (width * 0.874, height * 0.923), fontid="tiny")
    showtext(f"{str(devices['engine_main']).zfill(3)}", (width * 0.8745, height * 0.938), fontid="tiny")
    showtext("空速", (width * 0.844, height * 0.923), fontid="tiny")
    showtext(f"{str(sensors['speed']).zfill(3)}", (width * 0.8445, height * 0.938), fontid="tiny")
    showtext("能量", (width * 0.814, height * 0.923), fontid="tiny")
    showtext(f"{str(sensors['battery'] * 100).zfill(2)}%", (width * 0.8145, height * 0.938), fontid="tiny")
def netproc():
    while running:
        update()
        transmit("cmd", cmdgen())
        time.sleep(0.05)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    vdist = 30 # 虚拟视距
    lwidth = 60 # 水平指示器距离
    vwidth = lwidth * 0.5 / 0.76 # 竖直指示器距离
    # 网络初始化
    remote = lib.Net(dest = "127.0.0.1", port = 40808)
    # 数据初始化
    devices = dict()
    vangle = None
    langle = None
    for i in remote.jdata['devices'].keys():
        devices[i] = 0
    remote_devices = dict()
    for i in remote.jdata['devices'].keys():
        remote_devices[i] = 0
    sensors = dict()
    for i in remote.jdata['sensors'].keys():
        sensors[i] = 0
    name = remote.name
    # 摄像头初始化
    if camera_enabled:
        camera = cv2.VideoCapture(1)
    # 图形初始化
    pygame.init()
    pygame.display.set_caption(f"Azure 远程终端 - 连接到 {name}")
    flamenum = 0
    colors = {"main":"white", "remote":"green", "warn":"red"}
    fonts = {"medium":pygame.font.Font('src/font.ttf', 20), "big":pygame.font.Font('src/font.ttf', 40), "huge":pygame.font.Font('src/font.ttf', 60), "small":pygame.font.Font('src/font.ttf', 16), "tiny":pygame.font.Font('src/font.ttf', 12)}

    height = 1080
    width = int(height / 9 * 16)
    heightp = 1080
    widthp = int(height / 9 * 16)

    screen = pygame.display.set_mode((width, height), RESIZABLE)
    icon = pygame.image.load("src/icon.ico").convert_alpha()
    pygame.display.set_icon(icon)
    clock = pygame.time.Clock()
    running = True
    pygame.mouse.set_visible(False)
    pygame.mouse.set_pos([width / 2, height / 2])
    f_shootmode = 0

    #welcome()
    isfullscreen = 0
    camera_refresh()
    mousepos = (width / 2, height / 2)
    np = threading.Thread(target=netproc, name='NetworkProcessing')
    np.start()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                #loggin.info(mousepos)
                #loggin.info("鼠标: ", event.pos[0] - mousepos[0], event.pos[1] - mousepos[1])
                mousepos = event.pos
            if event.type == pygame.VIDEORESIZE:
                height = event.size[1]
                width = event.size[0]
                screen = pygame.display.set_mode((width, height), RESIZABLE)
        flamenum += 1
        if flamenum % 2 == 1:
            camera_refresh()
        screen.blit(frame_surface, (0, 0))
        # 计算
        vangle = calc_vangle(mousepos[1])
        langle = calc_langle(mousepos[0])
        # 常态指示器
        showline((width * 0.08, height * 0.75), (width * 0.08, height * 0.25), 2) # 高度指示
        showline((width * 0.92, height * 0.75), (width * 0.92, height * 0.25), 2) # 高度指示
        showline((width * 0.97, height * 0.86), (width * 0.95, height * 0.86), 2) # 翼面指示 1
        showline((width * 0.97, height * 0.90), (width * 0.95, height * 0.90), 2) # 翼面指示 2
        showline((width * 0.94, height * 0.86), (width * 0.92, height * 0.86), 2) # 翼面指示 1
        showline((width * 0.94, height * 0.90), (width * 0.92, height * 0.90), 2) # 翼面指示 2
        showline((width * 0.88, height * 0.1), (width * 0.12, height * 0.1), 2) # 方向指示
        showline((width / 2 - 20, height / 2), (width / 2 + 20, height / 2), 1 if not f_shootmode else 3, 'main' if not f_shootmode else 'warn') # 准星指示
        showline((width / 2, height / 2 + 20), (width / 2, height / 2 - 20), 1 if not f_shootmode else 3, 'main' if not f_shootmode else 'warn') # 准星指示

        for i in range(0, 9):
            showline((width * 0.92, height * 0.25 + height * 0.5 * i / 8), (width * 0.91, height * 0.25 + height * 0.5 * i / 8), 2) # 高度指示
            showline((width * 0.08, height * 0.25 + height * 0.5 * i / 8), (width * 0.09, height * 0.25 + height * 0.5 * i / 8), 2) # 高度指示

        for i in range(0, 13):
            showline((width * 0.12 + width * 0.76 * i / 12, height * 0.1), (width * 0.12 + width * 0.76 * i / 12, height * 0.1 + width * 0.01), 2) # 水平指示

        # 鼠标复位
        # pygame.mouse.set_pos([width / 2, height / 2])

        # 指示器
        dyna1 = ((width * 0.97, height * 0.86 - width * 0.01 * math.tan(math.radians(vangle)) + width * 0.01 * math.tan(math.radians(langle))), 
                (width * 0.95, height * 0.86 + width * 0.01 * math.tan(math.radians(vangle)) - width * 0.01 * math.tan(math.radians(langle))))
        dyna2 = ((width * 0.97, height * 0.90 - width * 0.01 * math.tan(math.radians(vangle)) + width * 0.01 * math.tan(math.radians(langle))), 
                (width * 0.95, height * 0.90 + width * 0.01 * math.tan(math.radians(vangle)) - width * 0.01 * math.tan(math.radians(langle))))
        dyna3 = ((width * 0.94, height * 0.86 - width * 0.01 * math.tan(math.radians(vangle)) - width * 0.01 * math.tan(math.radians(langle))), 
                (width * 0.92, height * 0.86 + width * 0.01 * math.tan(math.radians(vangle)) + width * 0.01 * math.tan(math.radians(langle))))
        dyna4 = ((width * 0.94, height * 0.90 - width * 0.01 * math.tan(math.radians(vangle)) - width * 0.01 * math.tan(math.radians(langle))), 
                (width * 0.92, height * 0.90 + width * 0.01 * math.tan(math.radians(vangle)) + width * 0.01 * math.tan(math.radians(langle))))

        
        showline(dyna1[0], dyna1[1], 2) # 翼面指示 1
        showline(dyna2[0], dyna2[1], 2) # 翼面指示 2
        showline(dyna3[0], dyna3[1], 2) # 翼面指示 1
        showline(dyna4[0], dyna4[1], 2) # 翼面指示 2

        showline((width * 0.97, height * 0.86 + math.tan(math.radians(remote_devices['aile_left'])) * 0.01 * width), 
                (width * 0.95, height * 0.86 - math.tan(math.radians(remote_devices['aile_left'])) * 0.01 * width), 2, color="remote") # 翼面指示 1
        showline((width * 0.97, height * 0.90 + math.tan(math.radians(remote_devices['aile_right'])) * 0.01 * width), 
                (width * 0.95, height * 0.90 - math.tan(math.radians(remote_devices['aile_right'])) * 0.01 * width), 2, color="remote") # 翼面指示 1
        showline((width * 0.94, height * 0.86 + math.tan(math.radians(remote_devices['tail_left'])) * 0.01 * width), 
                (width * 0.92, height * 0.86 - math.tan(math.radians(remote_devices['tail_left'])) * 0.01 * width), 2, color="remote") # 翼面指示 1
        showline((width * 0.94, height * 0.90 + math.tan(math.radians(remote_devices['tail_right'])) * 0.01 * width), 
                (width * 0.92, height * 0.90 - math.tan(math.radians(remote_devices['tail_right'])) * 0.01 * width), 2, color="remote") # 翼面指示 1
        showline((width * 0.88, height * 0.92), (width * 0.88, height * 0.92 - devices['engine_main']), 20, color="main") # 转速指示 1
        showline((width * 0.88, height * 0.92), (width * 0.88, height * 0.92 - remote_devices['engine_main']), 16, color="remote") # 转速指示 2
        showline((width * 0.849, height * 0.92), (width * 0.849, height * 0.92 - sensors["speed"]), 20, color="remote") # 空速指示 1
        showline((width * 0.82, height * 0.92), (width * 0.82, height * 0.92 - 100), 20, color="main") # 能量指示 2
        showline((width * 0.82, height * 0.92), (width * 0.82, height * 0.92 - sensors["battery"] * 100), 16, color="remote") # 能量指示 1
        
        devices['aile_left'] = calc_pair2angle(dyna1)
        devices['aile_right'] = calc_pair2angle(dyna2)
        devices['tail_left'] = calc_pair2angle(dyna3)
        devices['tail_right'] = calc_pair2angle(dyna4)
        
        text_layer()
    # 键盘事件
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = 0
        if keys[pygame.K_r]:
            pygame.mouse.set_pos([width / 2, height / 2])
        if keys[pygame.K_w]:
            pygame.mouse.set_pos([mousepos[0], mousepos[1] + 3])
        if keys[pygame.K_s]:
            pygame.mouse.set_pos([mousepos[0], mousepos[1] - 3])
        if keys[pygame.K_a]:
            pygame.mouse.set_pos([mousepos[0] - 3, mousepos[1]])
        if keys[pygame.K_d]:
            pygame.mouse.set_pos([mousepos[0] + 3, mousepos[1]])
        if keys[pygame.K_LSHIFT]:
            devices['engine_main'] += 1
        if keys[pygame.K_LCTRL]:
            devices['engine_main'] -= 1
        if keys[pygame.K_1]:
            warn_layer("失速警告")
        if keys[pygame.K_2]:
            warn_layer("失控")
        if keys[pygame.K_3]:
            warn_layer("通讯异常")
        if keys[pygame.K_4]:
            warn_layer("不明硬件损毁")
        if keys[pygame.K_5]:
            warn_layer("紧急重启")
        if keys[pygame.K_6]:
            warn_layer("紧急停机")
        if keys[pygame.K_7]:
            warn_layer("紧急关闭")
        if keys[pygame.K_8]:
            warn_layer("紧急过载")
        if keys[pygame.K_9]:
            warn_layer("操纵面失控")
        if keys[pygame.K_0]:
            warn_layer("引擎失控")
        if keys[pygame.K_F11]:
            if not isfullscreen:
                isfullscreen = True
                width = widthp
                height = heightp
                SIZE = width, height =  pygame.display.list_modes()[0]
                screen = pygame.display.set_mode(SIZE, FULLSCREEN)
            else:
                isfullscreen = False 
                screen = pygame.display.set_mode((width, height), RESIZABLE)
        if keys[pygame.K_b]:
            colors["main"] = "white"
        if keys[pygame.K_n]:
            colors["main"] = "blue"
        if keys[pygame.K_m]:
            colors["main"] = "green"
        if keys[pygame.K_v]:
            colors["main"] = "red"
        # 文字显示
        # debug
        debug_ui()
        pygame.draw.circle(screen, colors['main' if not f_shootmode else 'warn'], mousepos, 2)
        pygame.draw.circle(screen, colors['main'], mousepos, 20, 3) if not f_shootmode else ''
        # flip() the display to put your work on screen
        pygame.display.flip()
        showline((width * 0.88, height * 0.92), (width * 0.88, height * 0.92 - devices['engine_main']), 20) # 转速指示 1
        showline((width * 0.88, height * 0.92), (width * 0.88, height * 0.92 - remote_devices['engine_main']), 16, color="remote") # 转速指示 2
        showline((width * 0.849, height * 0.92), (width * 0.849, height * 0.92 - sensors['speed']), 20, color="remote") # 空速指示 2
        showline((width * 0.88, height * 0.92), (width * 0.88, height * 0.92 - devices['engine_main']), 20) # 转速指示 1
        showline((width * 0.88, height * 0.92), (width * 0.88, height * 0.92 - remote_devices['engine_main']), 16, color="remote") # 转速指示 2
        showline((width * 0.849, height * 0.92), (width * 0.849, height * 0.92 - sensors['speed']), 20, color="remote") # 空速指示 2
        
        dt = clock.tick(60) / 1000

    np.join()
    pygame.quit()
