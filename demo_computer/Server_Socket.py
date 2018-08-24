import socket
import threading
import Server_GUI
import os
import cv2
import numpy as np
from scipy.linalg import solve
import math
import time
import client

TCP_IP = ''
TCP_PORT = 1234
send_msg = ''
camera_port = 1
rec_result = ''

co = 0  # counter of points by mouse when initialize the coordinate
x = 0.000
y = 0.000
'''
●(0,0)  ●(32,0)


●(0,32)
'''
px = [0.000]  # array to store the input x coordinate when initialize 
py = [0.000]  # array to store the input y coordinate when initialize
rx = [0.000, 4.000, 0.000]  # 初始化的3個點的真實x座標（比例尺）
ry = [0.000, 0.000, 4.000]  # 初始化的3個點的真實y座標（比例尺）
t = 0
tx1, ty1, tx2, ty2, sx1, sy1, sx2, sy2 = 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000
solx, soly = 0.000, 0.000

before_pos = []

class ReceiveThread(threading.Thread):
    def __init__(self, s, count):
        threading.Thread.__init__(self)
        self.cs = s
        self.gui = Server_GUI.GUI()
        Server_GUI.iscreate2 = True

        if count == 0:
            # initialize first position of every thing in the room
            vcap = cv2.VideoCapture(camera_port)
            self.rret, self.rframe = vcap.read()
            cv2.imwrite('init_recog.jpg', self.rframe)
            self.cli = client.client_socket()
            init = threading.Thread(target=self.cli.create, args = ('init_recog.jpg', True))
            init.start()
            
            # initialize the coordinate
            cv2.namedWindow('image')
            cv2.setMouseCallback('image', self.draw_circle)
            # self.img = cv2.imread('tmpdemo.jpg')
            while(1):
                cv2.imshow('image', self.rframe)
                # cv2.imshow('image', self.img)
                k = cv2.waitKey(1)
                if co == 3:
                    cv2.destroyAllWindows()
                    break
            cv2.imwrite('init_coor.jpg', self.rframe)
            
            init.join()
            print('initial object recognition: ', before_pos, '\n')

    def run(self):
        while True:
            self.recv_msg = self.cs.recv(1024)
            if not self.recv_msg:
                break
            else:
                if self.validCommand(self.recv_msg.decode('utf-8')) > 0:
                    if self.validCommand(self.recv_msg.decode('utf-8')) != 3:
                        self.cs.send('正在進行辨識\n'.encode('utf-8'))

                    if os.path.isfile('./output.jpg'):
                        os.system('rm output.jpg')

                    cap = cv2.VideoCapture(camera_port)
                    if not cap.isOpened():
                        cap.open()

                    # save the 70th frame (for brightness of the image)
                    frameindex = 0
                    while True:
                        ret, frame = cap.read()
                        # cv2.imshow('frame', frame)
                        if frameindex == 70:
                            cv2.imwrite('output.jpg', frame)
                            break
                        frameindex += 1

                    cap.release()
                    cv2.destroyAllWindows()

                    # receiving result from workstation server
                    self.cli = client.client_socket()
                    rec_result = self.cli.create('output.jpg', False)
                    result_list = rec_result.split()
                    
                    # result back to app
                    if len(result_list) < 3:
                        self.cs.send('無辨識結果\n'.encode('utf-8'))
                    else:
                        if self.validCommand(self.recv_msg.decode('utf-8')) == 1:  # 有沒有移動過
                            if self.isMoved(self.obj, before_pos, result_list) == 1:
                                self.cs.send('沒有'.encode('utf-8'))
                                self.cs.send(self.translateEtoC(self.obj).encode('utf-8'))
                                self.cs.send('的辨識結果\n'.encode('utf-8'))
                            elif self.isMoved(self.obj, before_pos, result_list) == 2:
                                self.cs.send(self.translateEtoC(self.obj).encode('utf-8'))
                                self.cs.send('有移動過\n'.encode('utf-8'))
                            else:
                                self.cs.send(self.translateEtoC(self.obj).encode('utf-8'))
                                self.cs.send('沒有移動過\n'.encode('utf-8'))

                        elif self.validCommand(self.recv_msg.decode('utf-8')) == 2:  # 在哪裡
                            for index, rl in enumerate(result_list):
                                # print(rl, self.obj)
                                if rl == self.obj:
                                    objdir = self.direction(result_list[index+1], result_list[index+2])
                                    origin = self.four(320, 480)  # calculate coordinate of (320,480)     
                                    realxy = self.four(int(float(result_list[index+1])), int(float(result_list[index+2])))
                                    objdis = self.distance(realxy[0], realxy[1], origin[0], origin[1])
                                    step = math.ceil(objdis / 4)

                                    # sample:椅子大約在你的左前方五步 並在導盲杖可觸及的範圍內
                                    self.cs.send(self.translateEtoC(self.obj).encode('utf-8'))    
                                    self.cs.send('大約在你的'.encode('utf-8'))
                                    self.cs.send(objdir.encode('utf-8'))
                                    self.cs.send(str(step).encode('utf-8'))
                                    self.cs.send('步，並在導盲杖可觸及的範圍內\n'.encode('utf-8'))
                                    break
                                
                                elif index == len(result_list) - 1: 
                                    self.cs.send('沒有'.encode('utf-8'))
                                    self.cs.send(self.translateEtoC(self.obj).encode('utf-8'))
                                    self.cs.send('的辨識結果\n'.encode('utf-8'))
                        elif self.validCommand(self.recv_msg.decode('utf-8')) == 3:  # 紀錄家具位置
                            self.cs.send('傢俱位置紀錄完畢\n'.encode('utf-8'))

                    # update before_pos[]
                    rl = 0
                    while (rl+1) * 3 <= len(result_list):
                        same = False
                        for bp in before_pos:
                            if result_list[rl*3] == bp[0]:
                                same = True
                                bp[1] = result_list[rl*3+1]
                                bp[2] = result_list[rl*3+2]
                        if not same:
                            tmp = []
                            tmp.append(result_list[rl*3])
                            tmp.append(result_list[rl*3+1])
                            tmp.append(result_list[rl*3+2])
                            before_pos.append(tmp)
                        rl += 1 
                    print('updated object: ', before_pos, '\n')
                        
                else:
                    send_msg = '指令錯誤 請重新輸入\n'
                    self.cs.send(send_msg.encode('utf-8'))

                # self.gui.text_change('client: ' + self.recv_msg.decode('utf-8'))

    def draw_circle(self, event, x, y, flags, param):
        global ix, iy, co, tx1, tx2, ty1, ty2, px, py, sx1, sx2, sy1, sy2
        ix, iy = 0.000, 0.000
        if event == cv2.EVENT_LBUTTONDOWN:
            ix, iy = x, y
            cv2.rectangle(self.rframe, (ix, iy), (x, y), (0, 255, 0), 4)
            # cv2.rectangle(self.img, (ix, iy), (x, y), (0, 255, 0), 4)
            px.append(ix)
            py.append(iy)
            co = co+1
            if(co == 3):
                print('initial coordinate: '
                      '(', px[1], ',', py[1], ')'
                      '(', px[2], ',', py[2], ')'
                      '(', px[3], ',', py[3], ')')
                # convert coordinate
                sx1 = rx[1] - rx[0]
                sy1 = ry[1] - ry[0]
                sy2 = ry[2] - ry[0]
                sx2 = rx[2] - rx[0]
                tx1 = px[2] - px[1]
                ty1 = py[2] - py[1]
                tx2 = px[3] - px[1]
                ty2 = py[3] - py[1]

    def four(self, xx, yy):  # get the real coordinate of the 4th point
        global t, t1, t2  
        ix, iy = xx, yy

        if xx == 320 and yy == 480:
            t1 = 320 - px[1]
            t2 = 480 - py[1]
        else:
            px.append(ix)
            py.append(iy)
            t1 = px[4+t]-px[1]
            t2 = py[4+t]-py[1]
            # print(xx, yy, px[4+t], py[4+t], t1, t2) 
            t = t + 1

        a = np.array([[tx1, tx2], [ty1, ty2]])
        b = np.array([t1, t2])
        c = solve(a, b)
        return c

    def direction(self, xx, yy):
        xx, yy = int(float(xx)), (-1)*int(float(yy))
        # (x1,y1), (x2,y2) are points on the line, (xx,yy) is point to be checked
        if xx > 320:
            x1, y1 = 320, -480
            x2, y2 = 640, -295  # the two points on the 30 degree line
            x3, y3 = 597, 0  # the two points on the 60 degree line
            cal_30 = ((xx-x1) * (y2-y1)) - ((yy-y1) * (x2-x1))
            if cal_30 > 0:
                return "右手邊"
            else:
                cal_60 = ((xx-x1) * (y3-y1)) - ((yy-y1) * (x3-x1))
                if cal_60 > 0:
                    return "右前方"
                else:
                    return "前方"
        elif xx <= 320:
            x1, y1 = 320, -480
            x2, y2 = 0, -295
            x3, y3 = 43, 0
            cal_30 = ((xx-x1) * (y2-y1)) - ((yy-y1) * (x2-x1))
            if cal_30 <= 0:
                return "左手邊"
            else:
                cal_60 = ((xx-x1) * (y3-y1)) - ((yy-y1) * (x3-x1))
                if cal_60 > 0:
                    return "前方"
                else:
                    return "左前方"
        
    def distance(self, x1, y1, x2, y2):
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        xdis = x1 - x2
        ydis = y1 - y2
        real_xdis = xdis * (sx1 + sx2)
        real_ydis = ydis * (sy1 + sy2)
        tot_dis = pow((pow(real_xdis, 2) + pow(real_ydis, 2)), 0.5)
        return int(tot_dis)

    def translateEtoC(self, s):
        if s == 'fan':
            return '電風扇'
        elif s == 'chair':
            return '椅子'
        elif s == 'diningtable':
            return '桌子'
        elif s == 'box':
            return '箱子'
        elif s == 'dehumidifier':
            return '除溼機'
        elif s == 'sweepingrobot':
            return '掃地機器人'
        else:
            return s
    
    def translateCtoE(self, s):
        if s == '電風扇' or s == '電扇':
            return 'fan'
        elif s == '椅子' or s == '一直':
            return 'chair'
        elif s == '桌子':
            return 'diningtable'
        elif s == '箱子':
            return 'box'
        elif s == '除溼機':
            return 'dehumidifier'
        elif s == '掃地機器人':
            return 'sweepingrobot'
        else:
            return s

    def validCommand(self, s): # check if the input commands are valid
        if s[-6:] == '有沒有移動過':
            self.obj = s[:len(s)-6]
            self.obj = self.translateCtoE(self.obj)
            return 1
        elif s[-3:] == '在哪裡':
            self.obj = s[:len(s)-3]
            self.obj = self.translateCtoE(self.obj)
            return 2
        elif s == '記錄家具位置':
            return 3
        else:
            return 0

    def isMoved(self, s, before_pos, result_list):
        before = []
        after = []
        for bp in before_pos:
            if bp[0] == self.obj:
                before = [bp[1], bp[2]]
                break
        for index, rl in enumerate(result_list):
            if rl == self.obj:
                after = [result_list[index+1], result_list[index+2]]
                break

        if before == [] or after == []: # object not detected
            return 1
        elif abs(float(before[0]) - float(after[0])) > 30 or abs(float(before[1]) - float(after[1])) > 30:  # moved
            return 2
        else:  # not moved 
            return 3

class Socket:
    def __init__(self):
        self.sock = None
        Server_GUI.iscreate1 = True

    def create(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((TCP_IP, TCP_PORT))
        self.sock.listen(1)
        count = 0
        print('Wait for connection...')
        while True:
            self.s, addr = self.sock.accept()
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print('Connection address:', addr)
            receive = ReceiveThread(self.s, count)
            receive.start()
            count += 1

    def ssend(self):
        print('> ' + send_msg, end = '')
        self.s.send(send_msg.encode('utf-8'))
