import cv2
import numpy as np
from scipy.linalg import solve
import math
co = 0
x = 0.000
y = 0.000
px = [0.000]
py = [0.000]
rx = [0.000, 2.000, 0.000]
ry = [0.000, 0.000, 2.000]
t = 0
tx1, ty1, tx2, ty2, sx1, sy1, sx2, sy2 = 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000
solx, soly = 0.000, 0.000


def draw_circle(event, x, y, flags, param):
    global ix, iy, co, tx1, tx2, ty1, ty2, px, py, sx1, sx2, sy1, sy2
    ix, iy = 0.000, 0.000
    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 5)
        px.append(ix)
        py.append(iy)
        co = co+1
        if(co == 3):
            print(px)
            sx1 = rx[1]-rx[0]
            sy1 = ry[1]-ry[0]
            sx2 = rx[2]-rx[0]
            sy2 = ry[2]-ry[0]
            tx1 = px[2]-px[1]
            ty1 = py[2]-py[1]
            tx2 = px[3]-px[1]
            ty2 = py[3]-py[1]


def four(xx, yy):
    img = cv2.imread("output.jpg")
    cv2.namedWindow('image')
    global t, t1, t2
    ix, iy = xx, yy
    cv2.rectangle(img, (ix, iy), (xx, yy), (0, 255, 0), 5)
    cv2.imshow('image', img)
    px.append(ix)
    py.append(iy)
    t1 = px[4+t]-px[1]
    t2 = py[4+t]-py[1]
    print(tx1, ty1)
    a = np.array([[tx1, tx2], [ty1, ty2]])
    b = np.array([t1, t2])
    c = solve(a, b)
    # solve function
    print("x' , y ':", c)
    solx = c[0]*(sx1+sx2)
    soly = c[1]*(sy1+sy2)
    print("the real x:", ix, solx)
    print("the real y:", iy, soly)
    t = t+1


img = cv2.imread("output.jpg")
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)
while(1):
    cv2.imshow('image', img)
    k = cv2.waitKey(1)
    if co == 3:
        cv2.destroyAllWindows()
        break
four(300, 200)