import odbc
import tkinter
import tkinter.ttk


class SrcConnector(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.sourceselector = tkinter.ttk.Combobox()
        self.sourceselector.pack()

    def set_sources(self, sources):
        self.sourceselector.config(values=sources)


def init():
    a = tkinter.Tk()
    sources = odbc.get_sources()
    b = SrcConnector(a)
    b.set_sources(sources)
    b.mainloop()


init()