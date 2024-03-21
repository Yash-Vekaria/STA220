## Steps to Run Our Project:

In order to reproduce the code, follow the below steps:
1) Create a virtual environment using the ```virtualenv venv``` and activate it using ```source venv/bin/activate```. Then install the required libraries from the requirements.txt file using the command ```pip install -r requirements.txt```

Note: In order to start the web application, which already has all the visualization and sentiment analysis component included, go inside the front end directory and run the following command: ```flask run```

2) Create a database in your local machine and provide the credentials/info in ```Other_codes/db_utils.py``` and ```Spider_code/Crawler/pipelines.py```
3) Open YelpScraper.py (```Spider_code/Crawler/spiders/YelpScraper.py```)
4) Execute this file using the command ```scrapy crawl YelpScraper```
5) After the spider starts, and completes the crawling activity, loads data inside the database and closes, open the EDA_Notebook.ipynb file (```IPYNB_files/EDA_Notebook.ipynb```)
6) Click on ```Run all cells``` to recreate the visualisations the Data Analysis component of the project.
7) In order to run the Sentiment Analysis code, open the SentimentAnalyzer.py file, provide the link of the URL in the main function, for the variable ```restaurant_url``` (```Line 206```). (```Sentiment_Analysis/SentimentAnalyzer.py```) and execute the file.
