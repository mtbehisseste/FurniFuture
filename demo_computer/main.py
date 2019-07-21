import Server_GUI
import os

from tkinter import *

try:
    root = Tk()
    app = Server_GUI.GUI()
    root.title('Server')

    curWidth = root.winfo_width()
    curHeight = root.winfo_height()
    scnWidth, scnHeight = root.maxsize()
    tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
    root.geometry(tmpcnf)
    root.protocol("WM_DELETE_WINDOW", lambda: os._exit)
    root.mainloop()
except KeyboardInterrupt:
    root.destroy()
    os._exit
