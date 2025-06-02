import unittest
import time

from util.SQLiteDB import SQLiteDB


if __name__ == '__main__':
    db = SQLiteDB()
    db.init_db()
    db.insert_model_info(time.time(),model_info='{"da":1}')
