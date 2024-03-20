import scrapy
import sys
sys.path.insert(0, '/Users/akhilvelamati/Downloads/AdvDS-Analysis-master/venv/lib/python3.9/site-packages')


# Code for table creation in the database
class YelpItem(scrapy.Item):
    Name = scrapy.Field()
    Rating = scrapy.Field()
    Reviews = scrapy.Field()
    Price = scrapy.Field()
    Category = scrapy.Field()
    Address = scrapy.Field()
    City = scrapy.Field()
    Mon = scrapy.Field()
    Tue = scrapy.Field()
    Wed = scrapy.Field()
    Thu = scrapy.Field()
    Fri = scrapy.Field()
    Sat = scrapy.Field()
    Sun = scrapy.Field()

    def Start_Table_Creation_Process(self):
        return self["Name"] == "Creating_Required"

# Dropping a table if it already exists
    def drop_exist_table_sql(self):
        table_name = self["City"].replace(" ", "_")+"_Table"
        sql = f"DROP TABLE IF EXISTS {table_name}"
        return sql

# Code snippet to create a table
    def create_table_sql(self):
        table_name = self["City"].replace(" ", "_")+"_Table"
        #self.logger.info(table_name)
        sql = f"""CREATE TABLE {table_name}(
                              Name varchar(255),
                              Address varchar(255),
                              Category varchar(255),
                              Price varchar(255),
                              Rating varchar(255),
                              Reviews varchar(255),
                              Mon varchar(255),
                              Tue varchar(255),
                              Wed varchar(255),
                              Thu varchar(255),
                              Fri varchar(255),
                              Sat varchar(255),
                              Sun varchar(255) )"""
        return sql

# Code snippet to insert the scraped data into the tables
    def Insert_into_table_sql(self):
        table_name = self["City"].replace(" ", "_")+"_Table"
        category_string = ', '.join(self['Category'])
        sql = f"""INSERT INTO {table_name} (Name, Address, Category, Price, Rating, Reviews, Mon, Tue, Wed, Thu, 
                                      Fri, Sat, Sun) 
                                      VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        param = (self['Name'], self['Address'], category_string, self['Price'],
                 self['Rating'], self['Reviews'], self['Mon'], self['Tue'], self['Wed'],
                 self['Thu'], self['Fri'], self['Sat'], self['Sun'])
        return sql,param