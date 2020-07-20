from dataclasses import dataclass
from enum import Enum
import sqlite3
import pickle
import time
import os

class SavedQuery:
    def __init__(self):
        raise NotImplementedError()

@dataclass
class QueryResult:
    rows: int
    result: list
    time: float

    def __str__(self):
        return "<QueryResult object containing %s>" % self.result

    def get_one_column(self):
        return [i[0] for i in self.result]

class SavedStatus(Enum):
    SAVED = "saved"
    UNSAVED = "unsaved"

class Database:
    def __init__(self, path, statusbar = None):
        self.__connection = sqlite3.connect(path)
        self.statusbar = statusbar
        self.name = os.path.split(path)[-1]

        self.mark_as(SavedStatus.SAVED)

    def query(self, sql, args = ()):
        starttime = time.time()
        cursor = self.__connection.cursor()
        rows = cursor.execute(sql, args).rowcount
        result = cursor.fetchall()
        cursor.close()
        result = QueryResult(rows, result, time.time() - starttime)
        
        if self.statusbar is not None:
            self.statusbar.update_last_query(result.rows, result.time)
            if result.rows > 1:
                self.mark_as(status = SavedStatus.UNSAVED)

        return result

    def mark_as(self, status:SavedStatus):
        if status == SavedStatus.SAVED:
            self.savedStatus = SavedStatus.SAVED
            self.last_save = time.time()
            if self.statusbar is not None:
                self.statusbar.update_connected(self.name)
        else:
            self.savedStatus = SavedStatus.UNSAVED
            if statusbar is not None:
                self.statusbar.update_connected("*" + self.name)

    def commit(self):
        self.__connection.commit()
        self.mark_as(status = SavedStatus.SAVED)

    def close(self):
        print("Closed connection")
        self.__connection.close()

    def get_tables(self):
        return self.query("SELECT name FROM sqlite_master WHERE type = 'table';")

    def run_saved_query(self, saved_query:SavedQuery):
        raise NotImplementedError()

if __name__ == "__main__":
    db = Database("example_db.db")
    q = db.get_tables()
    print(q.time, q.rows, q)
    db.close()