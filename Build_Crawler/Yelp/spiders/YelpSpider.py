import sys
sys.path.insert(0, '/Users/akhilvelamati/Downloads/AdvDS-Analysis-master/venv/lib/python3.9/site-packages')
import scrapy
import re
from Yelp.items import YelpItem, ReviewItem
from urllib.parse import quote


class YelpSpider(scrapy.Spider):
    name = "YelpScraper"
    scrap_reviews = True

    # def start_requests(self):
    #     """
    #     choose the urls to start from
    #     """
    #     cities = []
    #     with open("/Users/akhilvelamati/Downloads/AdvDS-Analysis-master/Database/cities_csv/cities_of_CA.csv", "r") as f:
    #         for line in f:
    #             cities.append(line.strip())
    #     url_start = 'https://www.yelp.com/search?'
    #     # crawling the TOP 12 cities in California
    #     for city in cities[:12]:  # choose crawling cities
    #         search = 'restaurants'
    #         location = city + ', ' + 'CA'
    #         # url = url_start + 'find_desc=' + search + '&find_loc=' + location
    #         # yield scrapy.Request(url, meta={"city": city, "first_page": True}, callback=self.parse)
    #         url = url_start + 'find_desc=' + search + '&find_loc=' + location
    #         print("Constructed URL:", url)
    #         yield scrapy.Request(url, meta={"city": city, "first_page": True}, callback=self.parse)

    def start_requests(self):
        """
        choose the urls to start from
        """
        cities = []
        with open("/Users/akhilvelamati/Downloads/AdvDS-Analysis-master/Database/cities_csv/cities_of_CA.csv", "r") as f:
            for line in f:
                cities.append(line.strip())
        
        url_start = 'https://www.yelp.com/search?'

        # crawling the TOP 12 cities in California
        for city in cities[:12]:  # choose crawling cities
            self.logger.info(f"city is {city}")
            search = 'restaurants'
            location = city + ', ' + 'CA'
            encoded_location = quote(location)
            url = f"{url_start}find_desc={search}&find_loc={encoded_location}"
            
            self.logger.info(f"Constructed URL: {url}")
            
            yield scrapy.Request(url, meta={"city": city, "first_page": True}, callback=self.parse)

    def parse(self, response, scrap_reviews=scrap_reviews):
        """
        parse the search pages, crawl all of the urls of restaurants
        """
        self.logger.debug(f"Meta content: {response.meta}")
        self.logger.info("Starting Parse")
        city = response.meta["city"]
        if response.meta["first_page"]:
            self.logger.info("Entered if condition")
            # yield the item to create table in the database
            item = YelpItem()
            item["City"] = city
            item["Name"] = "table_start"
            yield item
            #self.logger.info(f"Data for first page - City: {item['City']}, Name: {item['Name']}")
            if scrap_reviews:
                self.logger.info("Started Review Part")
                item = ReviewItem()
                item["City"] = city
                item["Restaurant"] = "table_start"
                #self.logger.info(f"Review Item Data: {item}")
                yield item
        res = scrapy.Selector(response)
        #self.logger.info(f"SCRAPPY: {res}")
        place_urls = res.xpath("//h3/span[text()[contains(., '.')]]/a/@href").extract()
        self.logger.info(f"NeXT ONE:{place_urls}")
        for place_url in place_urls:
            url = "https://www.yelp.com" + place_url
            #url = place_url
            self.logger.info(f"Constructetfd URL: {url}")
            yield scrapy.Request(url, meta={"city": city}, callback=self.parse2)

        try:
            next_link = res.xpath("//a[contains(@class, 'next-link')]/@href").extract_first()
            #next_url = "https://www.yelp.com" + next_link
            next_url = next_link
            self.logger.info(f"afterlink:{next_url}")
            yield scrapy.Request(next_url, meta={"city": city, "first_page": False}, callback=self.parse)
        except TypeError:
            pass

    def parse2(self, response, scrap_reviews=scrap_reviews):
        """
        parse the restaurant pages, download the required information
        """
        #self.logger.debug(f"Meta content: {response.meta}")
        place = scrapy.Selector(response)
        #self.logger.debug(f"theplace: {place}")
        item = YelpItem()
        item["City"] = response.meta["city"]
        # item["Name"] = place.xpath("//div[@class = 'hidden']/div/meta[@itemprop = 'name']/@content").extract_first() \
        #     .replace("’", "'")
        # item["Rating"] = place.xpath("//div[@class = 'hidden']/div/div[@itemprop='aggregateRating']/meta/@content") \
        #     .extract_first()
        # item["Reviews"] = place.xpath("//div[@class = 'hidden']/div/div[@itemprop='aggregateRating']/span/text()") \
        #     .extract_first()
        # item["Price"] = place.xpath("//div[@class = 'hidden']/div/meta[@itemprop = 'priceRange']/@content") \
        #     .extract_first()
        # item["Category"] = ",".join(place.xpath("//h1/../../span[2]/span/a/text()").extract())
        # item["Address"] = ",".join(place.xpath("//div[@class = 'hidden']/div/address/span/text()").extract())
        # item["Name"] = place.xpath("//h1[@class='css-1se8maq']/text()").extract_first()
        # item["Rating"] = place.xpath("//a[contains(@class, 'css-19v1rkv')]/text()").extract_first()
        # #self.logger.info(f"RATED:{item['Rating']}")
        # item["Reviews"] = place.xpath("//span[@class='css-1fdy0l5']").extract_first()
        # #self.logger.info(f"RATED:{item['Rating']}")
        # item["Price"] = place.xpath("//span[@class='css-14r9eb']").extract_first()
        # item["Category"] = place.xpath("//a[@class='css-19v1rkv']").extract_first()
        # item["Address"] = place.xpath("//p[@class='css-qyp8bo']").extract_first()

        item["Name"] = place.xpath("//h1[@class='css-1se8maq']/text()").get()
        self.logger.info(f"NAMEIS:{item['Name']}")
        item["Rating"] = place.xpath("//a[contains(@class, 'css-19v1rkv')]/text()").get()
        #self.logger.info(f"RATED:{item['Rating']}")
        item["Reviews"] = place.xpath("//span[@class=' css-1fdy0l5']/text()").get()
        #self.logger.info(f"RATED:{item['Rating']}")
        item["Price"] = place.xpath("//span[@class=' css-14r9eb']/text()").get()
        a_elements = place.xpath("//span[@class=' css-1xfc281']//a[@class='css-19v1rkv']/text()").getall()
        # Process the text to remove unwanted characters like '&amp;'
        item["Category"]= [text.replace('&amp;', '&') for text in a_elements]
        #item["Category"] = place.xpath("//a[@class='css-19v1rkv']/text()").get()
        item["Address"] = place.xpath("//p[@class=' css-qyp8bo']/text()").get()


        # for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        #     item[day] = ",".join(place.xpath("//tr[@class='css-29kerx']//td[@class='css-1hgawz4']/ul/li/p[@class='no-wrap__09f24__c3plq']/text()".format(i + 1)).extract())

        # for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        #     day_selector = f"//p[contains(@class, 'day-of-the-week__09f24__JJea_') and text()='{day}']/ancestor::tr"
        #     opening_hours = place.xpath(f"{day_selector}//td[@class='css-1hgawz4']/ul/li/p[@class='no-wrap__09f24__c3plq']/text()").get()
        #     item[day] = opening_hours

        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            day_selector = f"//table[contains(@class, 'hours-table__09f24__KR8wh css-n604h6')]/tbody//th/p[contains(@class, 'day-of-the-week__09f24__JJea_ css-1p9ibgf') and text()='{day}']/../following-sibling::td/ul/li/p[@class='no-wrap__09f24__c3plq css-1p9ibgf']/text()"
            opening_hours = place.xpath(day_selector).get()
            if opening_hours is None:
                day_selector = f"//table[contains(@class, 'hours-table__09f24__KR8wh css-n604h6')]/tbody//th/p[contains(@class, 'day-of-the-week__09f24__JJea_ css-ux5mu6') and text()='{day}']/../following-sibling::td/ul/li/p[@class='no-wrap__09f24__c3plq css-1p9ibgf']/text()"
                opening_hours = place.xpath(day_selector).get()
            item[day] = opening_hours

        # pattern = re.compile(
        #     '"providerUrl":.*?,"label":"(.*?)","attributionText":.*?,"icon":.*?,"title":"(.*?)"')
        # amenities = re.findall(pattern, place.xpath("//script[@type = 'application/json']/text()")[2].extract())
        # for amenity in amenities:
        #     name = amenity[1].replace(" ", "_").replace("-", "_")
        #     amen_list = ["Delivery", "Wi_Fi", "Takes_Reservations", "Parking", "Vegetarian_Options",
        #                  "Accepts_Credit_Cards", "Accepts_Apple_Pay", "Accepts_Google_Pay", "Take_out"]
        #     if name in amen_list:
        #         item[name] = amenity[0]
        yield item

        if scrap_reviews:
            yield scrapy.Request(response.url,
                                 meta={"city": item["City"],
                                       "restaurant": item["Name"],
                                       "avg_rate": item["Rating"]},
                                 callback=self.parse3, dont_filter=True)

    def parse3(self, response):
        """
        parse every review page of the restaurant, download all of the reviews
        """
        item = ReviewItem()
        item["City"] = response.meta["city"]
        item["Restaurant"] = response.meta["restaurant"]
        item["Avg_rate"] = response.meta["avg_rate"]
        self.logger.info(f"Meta dataaa: {response.meta}")
        place = scrapy.Selector(response)
        pattern_str1 = (
            '"comment":{"text":"((?:.(?!"comment":))*?)","language"(?:.(?!"comment":))*?'
            '"rating":((?:.(?!"comment":))*?),"photosUrl"(?:.(?!"comment":))*?"funny":((?:.(?!"comment":))*?),'
            '"useful":((?:.(?!"comment":))*?),"cool":((?:.(?!"comment":))*?)},"userFeedback"(?:.(?!"comment":))*?'
            '"businessOwnerReplies".*?"reviewCount":(.*?),"altText".*?"friendCount":(.*?),"displayLocation":"(.*?)",'
            '"markupDisplayName":"(.*?)","userUrl".*?"photoCount":(.*?),"link".*?"localizedDate":"(.*?)"}'
        )
        pattern_str2 = (
            '"comment":{"text":"((?:.(?!"text":))*?)","language"(?:.(?!"text":))*?'
            '"rating":((?:.(?!"text":))*?),"photosUrl"(?:.(?!"text":))*?"funny":((?:.(?!"text":))*?),'
            '"useful":((?:.(?!"text":))*?),"cool":((?:.(?!"text":))*?)},"userFeedback"(?:.(?!"text":))*?'
            '"previousReviews":\\[.*?"isUpdated":true.*?"reviewCount":(.*?),"altText".*?"friendCount":(.*?),'
            '"displayLocation":"(.*?)","markupDisplayName":"(.*?)","userUrl".*?"photoCount":(.*?),'
            '"link".*?"localizedDate":"(.*?)"}'
        )
        pattern1 = re.compile(pattern_str1)
        pattern2 = re.compile(pattern_str2)
        html_str = place.xpath("//script[@type = 'application/json']/text()")[2].extract()
        self.logger.info(f"HTML string: {html_str}")
        reviews = re.findall(pattern1, html_str) + re.findall(pattern2, html_str)
        for review in reviews:
            self.logger.info(f"Review: {review}")
            item["Content"] = review[0]
            item["Review_rate"] = review[1]
            item["Funny"] = review[2]
            item["Useful"] = review[3]
            item["Cool"] = review[4]
            item["Review_Count"] = review[5]
            item["Friend_Count"] = review[6]
            item["Location"] = review[7]
            item["User_name"] = review[8]
            item["Total_photos"] = review[9]
            item["Review_time"] = review[10]
            yield item

        try:
            next_url = place.xpath("//link[@rel = 'next']/@href").extract_first()
            self.logger.info(f"Next URL: {next_url}")
            yield scrapy.Request(next_url,
                                 meta={"city": item["City"],
                                       "restaurant": item["Restaurant"],
                                       "avg_rate": item["Avg_rate"]},
                                 callback=self.parse3)
        except TypeError:
            pass

