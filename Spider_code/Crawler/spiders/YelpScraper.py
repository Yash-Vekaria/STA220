import sys
sys.path.insert(0, '/Users/av/Documents/GitHub/STA220/Spider_code')
import scrapy
import re
import os
from Crawler.items import YelpItem
from urllib.parse import quote


class YelpScraper(scrapy.Spider):
    name = "YelpScraper"
    scrap_reviews = True

    def start_requests(self):
        cities = []
        curr_path = os.path.abspath(os.path.join("..", "Stored_Info", "Locations", "CA.csv"))
        self.logger.info(f"PATH: {curr_path}")
        with open(curr_path, "r") as f:
            for line in f:
                cities.append(line.strip())
        
        url_start = 'https://www.yelp.com/search?'
        for city in cities[:12]:  
            self.logger.info(f"city is {city}")
            search = 'restaurants'
            location = city + ', ' + 'CA'
            encoded_location = quote(location)
            url = f"{url_start}find_desc={search}&find_loc={encoded_location}"
            self.logger.info(f"Constructed URL: {url}")
            yield scrapy.Request(url, meta={"city": city, "first_page": True}, callback=self.parse)

    def parse(self, response):
        self.logger.debug(f"Meta content: {response.meta}")
        city = response.meta["city"]
        if response.meta["first_page"]:
            self.logger.info("Entered if condition")
            item = YelpItem()
            item["City"] = city
            item["Name"] = "Creating_Required"
            yield item
            #self.logger.info(f"Data for first page - City: {item['City']}, Name: {item['Name']}")
            
        res = scrapy.Selector(response)
        #self.logger.info(f"SCRAPPY: {res}")
        place_urls = res.xpath("//h3/span[text()[contains(., '.')]]/a/@href").extract()
        self.logger.info(f"NeXT ONE:{place_urls}")
        for place_url in place_urls:
            url = "https://www.yelp.com" + place_url
            #url = place_url
            self.logger.info(f"Constructetfd URL: {url}")
            url_path = os.path.abspath(os.path.join("..", "Webpagefeatures", "restaurant_urls.txt"))
            f = open(url_path, "a+")
            f.write(f"{url}\n")
            f.close()
            yield scrapy.Request(url, meta={"city": city}, callback=self.parse2)

        try:
            next_link = res.xpath("//a[contains(@class, 'next-link')]/@href").extract_first()
            #next_url = "https://www.yelp.com" + next_link
            next_url = next_link
            self.logger.info(f"afterlink:{next_url}")
            yield scrapy.Request(next_url, meta={"city": city, "first_page": False}, callback=self.parse)
        except TypeError:
            pass

    def parse2(self, response):
        #self.logger.debug(f"Meta content: {response.meta}")
        place = scrapy.Selector(response)
        #self.logger.debug(f"theplace: {place}")
        item = YelpItem()
        item["City"] = response.meta["city"]

        item["Name"] = place.xpath("//h1[@class='css-hnttcw']/text()").get()
        self.logger.info(f"NAMEIS:{item['Name']}")
        item["Rating"] = place.xpath("//a[contains(@class, 'css-19v1rkv')]/text()").get()
        item["Reviews"] = place.xpath("//span[@class=' css-1fdy0l5']/text()").get()
        item["Price"] = place.xpath("//span[@class=' css-14r9eb']/text()").get()
        a_elements = place.xpath("//span[@class=' css-1xfc281']//a[@class='css-19v1rkv']/text()").getall()
        item["Category"]= [text.replace('&amp;', '&') for text in a_elements]
        item["Address"] = place.xpath("//p[@class=' css-qyp8bo']/text()").get()

        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            day_selector = f"//table[contains(@class, 'hours-table__09f24__KR8wh css-n604h6')]/tbody//th/p[contains(@class, 'day-of-the-week__09f24__JJea_ css-1p9ibgf') and text()='{day}']/../following-sibling::td/ul/li/p[@class='no-wrap__09f24__c3plq css-1p9ibgf']/text()"
            opening_hours = place.xpath(day_selector).get()
            if opening_hours is None:
                day_selector = f"//table[contains(@class, 'hours-table__09f24__KR8wh css-n604h6')]/tbody//th/p[contains(@class, 'day-of-the-week__09f24__JJea_ css-ux5mu6') and text()='{day}']/../following-sibling::td/ul/li/p[@class='no-wrap__09f24__c3plq css-1p9ibgf']/text()"
                opening_hours = place.xpath(day_selector).get()
            item[day] = opening_hours

        yield item
