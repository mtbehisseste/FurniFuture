import cv2
import numpy as np
from scipy.linalg import solve
import math

co = 0  # counter of points by mouse when initialize the coordinate
x = 0.000
y = 0.000
'''
●(0,0)  ●(32,0)


●(0,32)
'''
px = [0.000]  # array to store the input x coordinate when initialize 
py = [0.000]  # array to store the input y coordinate when initialize
rx = [0.000, 15.000, 0.000]  # 初始化的3個點的真實x座標（比例尺）
ry = [0.000, 0.000, 15.000]  # 初始化的3個點的真實y座標（比例尺）
t = 0
tx1, ty1, tx2, ty2, sx1, sy1, sx2, sy2 = 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000
solx, soly = 0.000, 0.000

def draw_circle(event, x, y, flags, param):
    global ix, iy, co, tx1, tx2, ty1, ty2, px, py, sx1, sx2, sy1, sy2
    ix, iy = 0.000, 0.000
    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 4)
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

            # draw_coor(img, px, py)

        if co > 3:
            objdir = direction(ix, iy)
            origin = four(320, 480)  # calculate coordinate of (320,480)
            realxy = four(int(float(ix)), int(float(iy)))
            objdis = distance(realxy[0], realxy[1], origin[0], origin[1])
            print(realxy, origin)   
            print('4th point x\' , y\':', realxy)
            print('objdir: ', objdir)
            print('distance to (320,480): ', objdis)

def four(xx, yy):  # get the real coordinate of the input point
    global t, t1, t2
    
    if xx == 320 and yy == 480:
        t1 = 320 - px[1]
        t2 = 480 - py[1]
    else:
        t1 = px[4+t]-px[1]
        t2 = py[4+t]-py[1]
        # print(xx, yy, px[4+t], py[4+t], t1, t2) 
        t = t + 1
        
    a = np.array([[tx1, tx2], [ty1, ty2]])
    b = np.array([t1, t2])
    c = solve(a, b)
    return c

def direction(xx, yy):
    xx, yy = int(float(xx)), (-1)*int(float(yy))
    # (x1,y1), (x2,y2) are points on the line, (xx,yy) is point to be checked
    if xx > 320:
        x1, y1 = 320, -480
        x2, y2 = 640, -160 # the two points on the 45 degree line
        cal = ((xx-x1) * (y2-y1)) - ((yy-y1) * (x2-x1))
        if cal <= 0:
            return "右前方"
        else:
            return "右手邊"
    elif xx < 320:
        x1, y1 = 320, -480
        x2, y2 = 0, -160
        cal = ((xx-x1) * (y2-y1)) - ((yy-y1) * (x2-x1))
        if cal <= 0:
            return "左手邊"
        else:
            return "左前方"
    else:
        return "前方"
    
def distance(x1, y1, x2, y2):
    x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
    xdis = x1 - x2
    ydis = y1 - y2
    real_xdis = xdis * (sx1 + sx2)
    real_ydis = ydis * (sy1 + sy2)
    tot_dis = pow((pow(real_xdis, 2) + pow(real_ydis, 2)), 0.5)
    return int(tot_dis)

# def draw_coor(img, px, py):
#     cv2.rectangle(img, (px[1], py[1]), (px[1], py[1]), (0, 0, 255), 4)
#     cv2.rectangle(img, (px[2], py[2]), (px[2], py[2]), (0, 0, 255), 4)
#     cv2.rectangle(img, (px[3], py[3]), (px[3], py[3]), (0, 0, 255), 4)
    # cv2.rectangle(img, (px[2] + px[2] - px[1], py[2] + py[2] - py[1]), (px[2] + px[2] - px[1], py[2] + py[2] - py[1]), (0, 0, 255), 4)
    # cv2.rectangle(img, (px[1] - px[2] + px[1], py[1] - py[2] + py[1]), (px[1] - px[2] + px[1], py[1] - py[2] + py[1]), (0, 0, 255), 4)
    # cv2.rectangle(img, (px[3] + px[3] - px[1], py[3] + py[3] - py[1]), (px[3] + px[3] - px[1], py[3] + py[3] - py[1]), (0, 0, 255), 4)
    # cv2.rectangle(img, (px[1] - px[2] + px[1], py[1] + py[3] - py[1]), (px[1] - px[2] + px[1], py[1] + py[3] - py[1]), (0, 0, 255), 4)
    # cv2.rectangle(img, (px[1] - px[2] + px[1], py[1] + py[3] - py[1]), (px[1] - px[2] + px[1], py[1] + py[3] - py[1]), (0, 0, 255), 4)

vcap = cv2.VideoCapture(1)
rret, img = vcap.read()
# img = cv2.imread('init_recog.jpg', 1)
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)
while(1):
    cv2.imshow('image', img)
    # if co == 3:
    #     cv2.destroyAllWindows()
    #     break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break