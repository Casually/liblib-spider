import sqlite3
import os
from util.file_util import file_util


class SQLiteDB:
    # 初始化数据库
    def __init__(self):
        conf = file_util.read_yml()
        self.db_path = os.path.join(conf.get('db')['path'], conf.get('db')['name'])

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS downloaded_models
                       (
                           model_uuid
                           TEXT
                           PRIMARY
                           KEY,
                           model_name
                           TEXT,
                           model_info
                           TEXT,
                           download_time
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')
        conn.commit()
        conn.close()

    def is_model_downloaded(self, model_uuid):
        if model_uuid is None:
            return True
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM downloaded_models WHERE model_uuid=?", (model_uuid,))
        result = cursor.fetchone()
        # print("查询结果：", result)
        conn.close()
        return result is not None

    def insert_model_info(self, model_uuid, model_name=None, model_info=None):
        if model_uuid is None:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO downloaded_models (model_uuid, model_name,model_info) VALUES (?, ?,?)",
                       (model_uuid, model_name, model_info,))
        conn.commit()
        conn.close()
