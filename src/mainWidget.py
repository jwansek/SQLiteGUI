import tkinter as tk
from tkinter import ttk
import abc
from dataclasses import dataclass
from enum import Enum

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

    @abc.abstractmethod
    def onopen(self, **kwargs):
        pass

class DefaultWindow(MainWidgetFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Text(self).pack(fill = tk.BOTH, expand = True)

    def onopen(self, **kwargs):
        pass

class SelectWindow(MainWidgetFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self, text = "SelectWindow").pack()
        self.lbl_table = tk.Label(self)
        self.lbl_table.pack()

    def onopen(self, **kwargs):
        assert "table" in kwargs.keys()
        self.lbl_table.config(text = kwargs["table"])

class UpdateWindow(MainWidgetFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self, text = "UpdateWindow").pack()
        self.lbl_table = tk.Label(self)
        self.lbl_table.pack()

    def onopen(self, **kwargs):
        assert "table" in kwargs.keys()
        self.lbl_table.config(text = kwargs["table"])

class DatabaseCommands(Enum):
    """This is the class through which we access all of the 
    different options of database commands. It also contains
    their associated frames.
    """
    SELECT = SelectWindow
    UPDATE = UpdateWindow