from tkinter import *
import Server_Socket

msg = ''
iscreate1 = False
iscreate2 = False

class GUI:
    def __init__(self):
        if iscreate1 is False:
            self.label1 = Label(text='IP address:', width=50)
            self.label1.grid()

            self.entry1 = Entry()
            self.entry1.grid()

            self.label3 = Label(text='port number:', width=50)
            self.label3.grid()

            self.entry3 = Entry()
            self.entry3.grid()

            self.btn1 = Button(command=self.btn1_event)
            self.btn1.grid()
            self.btn1.configure(text="Confirm")

            self.label4 = Label(text='', width=50)
            self.label4.grid()

            # self.label2 = Label(text="欲傳送的訊息:")
            # self.label2.grid()

            # self.entry2 = Entry(width=50)
            # self.entry2.grid()

            # self.btn2 = Button(command=self.btn2)
            # self.btn2.grid()
            # self.btn2.configure(text="Send")

        # if iscreate1 is True and iscreate2 is False:
            # self.text = Text(width=60)
            # self.text.grid()

    def btn1_event(self):
        Server_Socket.TCP_IP = self.entry1.get()
        Server_Socket.TCP_PORT = int(float(self.entry3.get()))
        self.entry1.config(state=DISABLED)
        self.entry3.config(state=DISABLED)
        # msg = 'waiting for connection...'
        # self.text_change(msg)
        self.ss = Server_Socket.Socket()
        self.ss.create()

    # def btn2(self):
    #     send_temp = self.entry2.get()
    #     if send_temp == '' or send_temp == ' ' or send_temp == '\n':
    #         pass
    #     else:
    #         send_temp = send_temp + '\n'
    #         Server_Socket.send_msg = send_temp
    #         self.entry2.delete('0', 'end')
    #         self.ss.ssend()

            #self.text.config(state=NORMAL)
            #self.text.insert(INSERT, 'Server: ' + msg + '\n')
            #self.text.config(state=DISABLED)

    # def text_change(self, msg):
    #     self.text.config(state=NORMAL)
    #     self.text.insert(INSERT, msg + '\n')
    #     self.text.config(state=DISABLED)

