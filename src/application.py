from enum import Enum
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as filedialogue
import database
import mainWidget
import sys
import os

class Application(tk.Tk):
    def __init__(self, dbpath = ":memory:", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("SQLiteGUI")

        # setup menubar
        self.menu = ApplicationMenu(self)
        self.config(menu = self.menu)

        self.mainpain = ttk.PanedWindow(self, orient = tk.HORIZONTAL)
        self.mainpain.pack(fill = tk.BOTH, expand = True, side = tk.TOP)

        self.tables_and_queries = TablesAndQueriesBook(self)
        self.mainpain.add(self.tables_and_queries)

        self.mainwidget = mainWidget.MainWidget(self)
        self.mainpain.add(self.mainwidget)
        # self.mainwidget.load_window("frame_a")

        ttk.Separator(self, orient = tk.HORIZONTAL).pack(fill = tk.X, pady = 3)

        self.db_statusbar = DatabaseStatusBar(self)
        self.db_statusbar.pack(fill = tk.X, side = tk.BOTTOM)

        # set up bindings etc, load the database
        self.use_database(dbpath)
        self.bind('<Control-o>', lambda a: self.open_database_file_gui())
        self.bind('<Control-s>', lambda a: self.save_database())
        self.protocol("WM_DELETE_WINDOW", self.exit)

    def use_database(self, path):
        self.db = database.Database(path, self.db_statusbar)
        self.tables_and_queries.tables_list.update_tables(self.db.get_tables().get_one_column())
        pass

    def new_database_gui(self):
        #TODO: throw a warning if unsaved
        raise NotImplementedError()

    def open_database_file_gui(self):
        #TODO: throw a warning if unsaved
        dia = filedialogue.askopenfilename(filetypes = (("SQLite files", ".db", ".sql"), ("All files", "*.*")))
        if os.path.exists(dia):
            self.use_database(dia)

    def save_database(self):
        self.db.commit()

    def save_database_as(self):
        raise NotImplementedError()

    def test_func(self):
        self.db.mark_as(database.SavedStatus.UNSAVED)

    def new_table_gui(self):
        raise NotImplementedError()

    def exit(self):
        if self.db is not None:
            self.db.close()

        self.destroy()

class ApplicationMenu(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.file_menu = tk.Menu(self, tearoff = 0)
        self.add_cascade(label = "File", menu = self.file_menu)
        self.file_menu.add_command(
            label = "New database", 
            accelerator = "Ctrl+N",
            command = self.parent.new_database_gui
        )
        self.file_menu.add_command(
            label = "Open database file...", 
            accelerator = "Ctrl+O",
            command = self.parent.open_database_file_gui
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label = "Save", 
            accelerator = "Ctrl+S",
            command = self.parent.save_database
        )
        self.file_menu.add_command(
            label = "Save As...", 
            accelerator = "Ctrl+Shift+S",
            command = self.parent.save_database_as
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label = "Exit", 
            accelerator = "Alt+F4",
            command = self.parent.exit
        )

        self.add_command(label = "Test", command = self.parent.test_func)     

class DatabaseStatusBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.lbl_right = tk.Label(self)
        self.lbl_right.pack(side = tk.RIGHT)
        self.lbl_left = tk.Label(self, text = "Not connected")
        self.lbl_left.pack(side = tk.LEFT)

    def update_connected(self, name):
        self.lbl_left.config(text = f"Connected to {name}")
        self.parent.title(f"{name} - SQLiteGUI")

    def update_last_query(self, rows, time):
        self.lbl_right.config(
            text = "Last query took %.4f seconds. %i rows affected" % (time, rows)
        )

class TablesAndQueriesBook(ttk.Notebook):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.tables_list = TablesList(self)
        self.add(self.tables_list, text = "Tables")

        self.queries_list = QueriesList(self)
        self.add(self.queries_list, text = "Queries")

class TablesList(tk.Frame):

    table_names = []

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.table = tk.Listbox(self)
        self.table.pack(fill = tk.BOTH, expand = True)

        ttk.Button(
            self, text = "New table...", command = self.parent.parent.new_table_gui
        ).pack(fill = tk.X)

        self.popup_menu = TablesListMenu(self, tearoff = False)
        self.table.bind("<Button-1>", self.draw_menu)

    def update_tables(self, tables):
        self.table_names = tables

        for table in tables:
            self.table.insert(0, table)

    def draw_menu(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()

    def get_selection(self):
        return self.table.get(self.table.curselection()[0])

class TablesListMenu(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        for option in mainWidget.DatabaseCommands:
            self.add_command(
                label = option.name, 
                command = lambda option=option: self.parent.parent.parent.mainwidget.raise_frame(
                    option.value, table=self.parent.get_selection()
                )
            )

class QueriesList(tk.Listbox):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

if __name__ == "__main__": 
    try:
        app = Application(sys.argv[1])
    except IndexError:
        app = Application()
    app.mainloop()