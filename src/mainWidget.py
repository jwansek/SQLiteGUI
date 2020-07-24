import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext 
import abc
from dataclasses import dataclass
from enum import Enum
import help_text

class MainWidget(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        
        container = tk.Frame(self)
        container.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self._frames = {}
        for F in [f.value for f in DatabaseCommands] + [DefaultWindow]:
            frame = F(container, self)
            self._frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = tk.NSEW)

        self.raise_frame(DefaultWindow)

    def __iter__(self):
        return iter(self._frames.values())

    def __getitem__(self, key):
        return self._frames[key]

    def raise_frame(self, frame, **kwargs):
        self._frames[frame].tkraise()
        self._frames[frame].onopen(**kwargs)
        self.current_frame = frame

@dataclass
class MainWidgetFrame(abc.ABC, tk.Frame):
    """Interface class that all frames of the main frame 
    must inherit from.
    """
    parent: tk.Frame
    controller: MainWidget

    def __post_init__(self):
        super().__init__(self.parent)

        self.sql_book = ttk.Notebook(self)
        self.sql_book.pack(fill = tk.BOTH, expand = True)

        self.info_text = scrolledtext.ScrolledText(self.sql_book, wrap = tk.WORD)
        self.sql_book.add(self.info_text, text = "Info")

    @abc.abstractmethod
    def onopen(self, **kwargs):
        pass

    def add_page(self, frame:tk.Frame, text:str, title:str):
        masterframe = ttk.PanedWindow(self, orient = tk.VERTICAL)
        masterframe.add(frame)

        bottom_text = scrolledtext.ScrolledText(self, wrap = tk.WORD, height = 3)
        bottom_text.insert(tk.END, text)
        bottom_text.config(state = tk.DISABLED)
        masterframe.add(bottom_text)

        self.sql_book.add(masterframe, text = title)

    def set_info_text(self, text):
        self.info_text.config(state = tk.NORMAL)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state = tk.DISABLED)

class DefaultWindow(MainWidgetFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.set_info_text("DefaultWindow")

    def onopen(self, **kwargs):
        pass

class SelectWindow(MainWidgetFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.set_info_text("SelectWindow")

        from_tables_frame = tk.Frame()
        tk.Label(from_tables_frame, text = "from_tables_frame").pack(fill = tk.BOTH, expand = True)

        self.add_page(from_tables_frame, text = help_text.HELP_TEXT["SELECT"]["Tables"], title = "Tables")

    


    def onopen(self, **kwargs):
        assert "table" in kwargs.keys()
        # self.lbl_table.config(text = kwargs["table"])

class UpdateWindow(MainWidgetFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.set_info_text("UpdateWindow")

    def onopen(self, **kwargs):
        assert "table" in kwargs.keys()
        # self.lbl_table.config(text = kwargs["table"])

class DatabaseCommands(Enum):
    """This is the class through which we access all of the 
    different options of database commands. It also contains
    their associated frames.
    """
    SELECT = SelectWindow
    UPDATE = UpdateWindow