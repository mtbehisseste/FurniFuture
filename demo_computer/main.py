import Server_GUI

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
    root.mainloop()
except KeyboardInterrupt:
    root.destroy()
