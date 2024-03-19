from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
import csv


def get_chrome_options_object():
	chrome_options = Options()
	# chrome_options.add_argument("--headless")
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')
	chrome_options.add_argument('--ignore-ssl-errors=yes')
	chrome_options.add_argument('--ignore-certificate-errors')
	chrome_options.add_argument("--window-size=1280,720")
	chrome_options.add_argument("--start-maximized")
	chrome_options.add_argument("--disable-blink-features=AutomationControlled")
	chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
	return chrome_options

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=get_chrome_options_object())

f = open("restaurant_urls.txt", "r")
restaurant_urls = [url.strip() for url in f.read().split("\n")]
f.close()

# Defining the headers for the CSV file
headers = ["name", "url", "amenities"]
with open("amenities_raw.csv", "w", newline='', encoding='utf-8') as file:
	writer = csv.writer(file)
	writer.writerow(headers)

for url in restaurant_urls[515:]:

	print(restaurant_urls.index(url), url)
	try:
		driver.get(url)
		# https://www.yelp.com/biz/starbird-chicken-san-francisco-2?osq=Restaurants
		name = driver.find_element(By.XPATH, "//h1[@class='css-hnttcw']").text
		print(name)
		driver.execute_script("window.scrollTo(0,document.body.scrollHeight/6.5)")

		# Click the button to reveal the amenities using XPath
		button_xpath = "//button//p[contains(text(), 'More Attributes')]"
		button = driver.find_element(By.XPATH, button_xpath)
		button.click()
		# sleep(5)

		# Extract amenities
		'''
		amenities_container_xpath = "//div[@id='expander-link-content-:Rjhecr:']"
		amenities_container = driver.find_element(By.XPATH, amenities_container_xpath)
		amenities = [amenity.strip() for amenity in str(amenities_container.text).split("\n")]
		print(amentities)
		'''
		# Find all elements that match the XPath
		elements = driver.find_elements(By.XPATH, "//section[contains(@aria-label, 'Amenities and More')]//div[contains(@class, 'arrange-unit')]/div/div/span[@data-font-weight='semibold']")

		# Filter elements by CSS color property target_color as those color represents amenities offered by the restaurant
		target_color = 'rgba(45, 46, 47, 1)'
		filtered_elements = [str(el.text).strip() for el in elements if el.value_of_css_property('color') == target_color]
		amenities = [str(el.text).strip() for el in elements]
		print(filtered_elements)
		print(amenities)
	except:
		sleep(10)
		continue

	# Appending details to the CSV file
	with open("amenities_raw.csv", "a", newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
		writer.writerow([name, url, "|".join(filtered_elements)])
	file.close()

	sleep(5)

# Close the driver
driver.quit()
