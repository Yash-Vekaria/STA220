import sys
# sys.path.insert(0, '/Users/av/Documents/Github/STA220/venv/lib/python3.9/site-packages')
#sys.path.insert(0, '/Users/yvekaria/Documents/PhD Course Work/STA 220 Data & Web Technologies for Data Science/Project/YelpTest/STA220/Spider_code')
from scrapy.exporters import CsvItemExporter
import pymysql
class DefaultValuesPipeline(object):
    def process_item(self, item, spider):
        for field in item.fields:
            item.setdefault(field, 'NULL')
        return item
    
class YelpPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host='localhost',port=3306,user='root',password='Purnaseshi128',database='yelp_db')
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        if item.Start_Table_Creation_Process():
            self.cursor.execute(item.drop_exist_table_sql())
            self.cursor.execute(item.create_table_sql())
            self.conn.commit()
        else:
            insert_sql, param = item.Insert_into_table_sql()
            self.cursor.execute(insert_sql, param)
            self.conn.commit()
    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()