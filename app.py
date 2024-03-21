from flask import Flask, render_template, request
import os
from time import sleep
from selenium import webdriver
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

os.environ['SSL_CERT_FILE'] = '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/certifi/cacert.pem'
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

app = Flask(__name__)

class SentimentAnalyzer():
    '''
    Class with defined functions to perform sentiment analysis of reviews
    '''

    def __init__(self, reviews):
        self.reviews = reviews
        self.sentiments = {}
        self.df = pd.DataFrame(columns=['review', 'sentiment'])

    def get_sentiment(self, review_text):
        '''
        Function to get sentiment of a review
        '''
        analysis = TextBlob(review_text)
        if analysis.sentiment.polarity > 0:
            return 'Positive'
        elif analysis.sentiment.polarity == 0:
            return 'Neutral'
        else:
            return 'Negative'

    def remove_stop_words(self, review_text):
        '''
        Function to remove stop words in the input review_text
        '''
        text_tokens = word_tokenize(review_text)
        text_without_sw = " ".join([word for word in text_tokens if not word in stopwords.words()])
        return text_without_sw

    def get_best_positive_best_negative_words(self):
        '''
        Function to get top words that represent positive reviews and the same for negative reviews
        '''
        data = [(review, sentiment) for review, sentiment in self.sentiments.items()]
        self.df = pd.DataFrame(data, columns=['review', 'sentiment'])

        target = [1 if self.df.loc[i, 'sentiment'] == "Positive" else 0 for i in range(len(self.df))]
        X = [self.remove_stop_words(self.df.loc[i,'review']) for i in range(len(self.df))]

        cv = CountVectorizer(binary=True)
        cv.fit(X)
        X = cv.transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X, target, train_size=0.7)

        final_model = LogisticRegression(C=0.05)
        final_model.fit(X_train, y_train)

        feature_to_coef = {word: coef for word, coef in zip(cv.get_feature_names_out(), final_model.coef_[0])}
        best_postive_words = sorted(feature_to_coef.items(), key=lambda x: x[1], reverse=True)[:20]
        best_negative_words = sorted(feature_to_coef.items(), key=lambda x: x[1])[:20]

        return best_postive_words, best_negative_words
    def generate_word_cloud(self, positive_words, negative_words):
        '''
        Function to generate two word clouds from the list of positive and negative words using their frequency distribution in review texts
        '''

        # Combine all reviews into a single string
        all_reviews = ' '.join([self.remove_stop_words(rev) for rev in self.reviews])

        # Calculate frequency distribution of the words
        word_freq_dist = nltk.FreqDist(nltk.word_tokenize(all_reviews.lower()))
        positive_freq = {word: word_freq_dist[word] for word in positive_words}
        negative_freq = {word: word_freq_dist[word] for word in negative_words}

        # Generate the word cloud for positive words
        positive_wordcloud = WordCloud(width=800, height=400, background_color='white')
        positive_wordcloud.generate_from_frequencies(positive_freq)
        positive_wordcloud.to_file('./static/Images/positive_wordcloud.png')

        # Generate the word cloud for negative words
        negative_wordcloud = WordCloud(width=800, height=400, background_color='white')
        negative_wordcloud.generate_from_frequencies(negative_freq)
        negative_wordcloud.to_file('./static/Images/negative_wordcloud.png')
        return
def scroll_page_to_explore(mydriver, scroll_pause_time, sleep_time, scroll_script):
    '''
    Function to scroll on the restaurant's yelp page to get reviews
    '''
    mydriver.execute_script(scroll_script)
    mydriver.execute_script(scroll_script)
    mydriver.execute_script(scroll_script)
    sleep(scroll_pause_time)
    sleep(sleep_time)
    return;

def get_reviews(url):
    '''
    Function to fetch reviews for the input restaurant URL
    '''

    options = Options()
    #options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-extensions")
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)

    restaurant_name = str(driver.find_element(By.XPATH, "//h1").text)
    precise_net_rating = str(driver.find_elements(By.XPATH, '//div[@data-testid="photoHeader"]//div[contains(@class, "arrange-unit")]//span[@data-font-weight="semibold"]')[0].text)
    precise_num_reviews = int(str(driver.find_element(By.XPATH, '//a[@href="#reviews"]').text).replace(" reviews)", "").replace("(", "").replace(",", ""))

    review_ratings = []
    reviews = []
    for i in range(5):

        scroll_page_to_explore(driver, 3, 1.5, "window.scrollTo(0, (document.body.scrollHeight)/(3));")
        scroll_page_to_explore(driver, 3, 1.5, "window.scrollTo(0, (document.body.scrollHeight)/(1.5));")
        scroll_page_to_explore(driver, 3, 1.5, "window.scrollTo(0, (document.body.scrollHeight)/(1.15));")

        temp_rating_elements = driver.find_elements(By.XPATH, '//section[@aria-label="Recommended Reviews"]//div/span/div[contains(@aria-label, " star rating")]')
        temp_review_ratings = [int(str(ele.get_attribute("aria-label")).replace(" star rating", "")) for ele in temp_rating_elements[1:]]
        temp_review_elements = driver.find_elements(By.XPATH, '//section[@aria-label="Recommended Reviews"]//p[contains(@class, "comment_")]//span[@lang="en"]')
        temp_reviews = [str(ele.text) for ele in temp_review_elements]

        if len(temp_review_ratings) == len(temp_reviews):
            review_ratings.extend(temp_review_ratings)
            reviews.extend(temp_reviews)

        arrow_buttons = driver.find_elements(By.XPATH, '//span[contains(@class, "navigation-button-icon")]')
        if len(arrow_buttons) == 2:
            arrow_buttons[1].click()
        else:
            break;

    review_to_ratings = {}
    for rev in reviews:
        ind = reviews.index(rev)
        if rev not in review_to_ratings.keys():
            review_to_ratings[rev] = review_ratings[ind]

    return restaurant_name, precise_net_rating, precise_num_reviews, review_to_ratings

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/visualization')
def visualization():
    # Pass any necessary data to the template
    return render_template('visualization.html')

@app.route('/sentiment_analysis', methods=['GET', 'POST'])
def sentiment_analysis():
    output = None
    if request.method == 'POST':
        # Handle form submission
        restaurant_link = request.form.get('restaurant_link')
        restaurant, ratings, reviews, recommended_reviews = get_reviews(restaurant_link)
        sa = SentimentAnalyzer(list(recommended_reviews.keys()))
        for review in sa.reviews:
            sa.sentiments[review] = sa.get_sentiment(review)
        num_positve_reviews = list(sa.sentiments.values()).count("Positive")
        num_negatve_reviews = list(sa.sentiments.values()).count("Negative")
        num_neutral_reviews = list(sa.sentiments.values()).count("Neutral")
        best_positive_words, best_negative_words = sa.get_best_positive_best_negative_words()
        positive_words = [str(word[0]) for word in best_positive_words]
        negative_words = [str(word[0]) for word in best_negative_words]
        output = {
            "restaurant": restaurant,
            "ratings": ratings,
            "reviews": reviews,
            "num_positve_reviews": num_positve_reviews,
            "num_negatve_reviews": num_negatve_reviews,
            "num_neutral_reviews": num_neutral_reviews,
            "positive_words": ', '.join(positive_words),
            "negative_words": ', '.join(negative_words)
        }
        sa.generate_word_cloud(positive_words, negative_words)
    return render_template('sentiment_analysis.html', output=output)

if __name__ == "__main__":
    app.run(debug=True)
