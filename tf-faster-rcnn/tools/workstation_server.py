'''
socket between android and demo computer use port 1234
socket between demo computer and workstation use port 8888
'''

import socket
import os
import threading
import sys

# sys.path.append('./tools')
# import demo
host = '192.168.0.107'
# host = '192.168.0.106'
port = 8888
address = (host, port)

def socket_service():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ss.bind(address)
        ss.listen(1)
    except socket.error as e:
        print (e)
        sys.exit(1)
    
    # empty folder
    if os.path.isfile('../data/demo/client_input.jpg'):
        os.system('rm ../data/demo/client_input.jpg')

    print('Waiting for connection...')

    while True:
        try:
            conn, addr = ss.accept()
            conn_ret, addr_ret = ss.accept()
            print('Connected to', addr)  
            
            # images to sent
            imgPath = os.getcwd() + '/../data/demo/'

            t = threading.Thread(target = img_receive, args = (conn, addr, imgPath, conn_ret))
            t.start()
        except KeyboardInterrupt:
            ss.close()
            sys.exit()

def img_receive(conn, addr, imgPath, conn_ret):
    while True:
        print('start receiving...')
        
        imgFile = open(imgPath + 'client_input.jpg', 'wb')
        while True:
            imgData = conn.recv(1024)

            if not imgData:
                break
            else:
                imgFile.write(imgData)
        imgFile.close()

        print ('Image has saved successfully!')

        os.system('cd .. && ./tools/demo.py')

        demo_result_ws = []
        f = open('../demo_result', 'r')
        line = f.readline()
        while line:
            demo_result_ws.append(line)
            line = f.readline()

        # socket return result back to demo computer
        print('list to send to client: ', demo_result_ws)
        for resindex in demo_result_ws:
            conn_ret.send(resindex.encode('utf-8'))
        print('\n')
        conn_ret.close()

        sys.exit()

if __name__ == '__main__':
    socket_service()
