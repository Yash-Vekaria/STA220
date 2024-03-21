import sys
import csv
import pandas as pd
sys.path.insert(0, '/Users/akhilvelamati/Downloads/AdvDS-Analysis-master/venv/lib/python3.9/site-packages')
sys.path.insert(0, '/usr/local/mysql/bin')
import pymysql

# Class for database functionality
class YelpDb:
    def __init__(self, db_name):
        self.host = "localhost"
        self.user = "root"
        self.password = "password"
        self.db = db_name
        self.charset = 'utf8'
        self.conn = pymysql.connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    db=self.db,
                                    charset=self.charset)
        self.cursor = self.conn.cursor()
        
# Functions to process commands
        
    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except pymysql.Error:
            self.conn.rollback()
            print(sql)

    def fetch_all(self):
        return self.cursor.fetchall()

    def fetch_one(self):
        return self.cursor.fetchone()
    
    def import_sql(self, sql_file_path):
        file = open(sql_file_path, encoding="utf8")
        sqls = " ".join(file.readlines())
        for sql in sqls.split(";"):
            self.cursor.execute(sql)
        self.conn.commit()

    def df_conversion(self, table_name):
        yelp_df = pd.read_sql(f"SELECT * FROM {table_name};", self.conn)
        return yelp_df
    
    def close(self):
        self.cursor.close()
        self.conn.close()
        