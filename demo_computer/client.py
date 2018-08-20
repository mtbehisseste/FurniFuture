'''
Structure:
demo_computer/
    clinet.py
tf-faster-rcnn/
    tools/
        demo.py
    graph_socket/
        server.py
    data/
        demo/
            {images received in server will be saved here}
    images/
        {images to send}

Images get by opencv will be saved in images folder.
client.py get images from images folder and sent to server.py.
server.py will saved images at data/demo/ for rcnn use.
'''

import socket
import os
import time
import Server_Socket

host = '140.115.52.195'
# host = '192.168.0.107'
port = 8888

create_result = ''

class client_socket:
    def __init__(self):
        self.address = (host, port)
        self.cs_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # for image sending
        self.cs_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # for receiving message from server

    def create(self, img, isFirst):
        create_result = self.socksock(self.address, self.cs_send, self.cs_recv, img)
        tmp = create_result.split('\n')
        if isFirst:
            for x in tmp:
                if x != '':
                    Server_Socket.before_pos.append(x.split())

        return create_result

    def socksock(self, address, cs_send, cs_recv, img):
        cs_send.connect(address)
        print ('Start sending image output.jpg')

        # images to sent
        imgFile = open(img, 'rb')
        # imgFile = open('output.jpg', "rb")

        while True:
            imgData = imgFile.readline(512)
            if not imgData:
                break
            cs_send.send(imgData)
        cs_send.close()
        imgFile.close()
        print('Finish sending image output.jpg')

        cs_recv.connect(address)
        result = cs_recv.recv(1024)
        # print('received from server: ' + result.decode())
        cs_recv.close()

        return result.decode()
