# GoogleReviewsCrawler

A python scraper that extracts the google reviews from a given Google Search term (“aspria berlin ku'damm” is used for testing).
Selenium is used to retrieve the link of the business reviews page in google and then the information regarding the reviews are scraped using Scrapy
and saved into a csv file.

The following information for all reviews of the target:\
Reviewer Name (text) \
Review content (text) \
Rating (int) \
Review Time Information (text) \
Did the shop owner reply (bool) \
Reply text from Owner (text) \

This crawler script can be found at review_scraper/review_scraper/spiders/google.py. Also contained in the spiders folder is a requirements.txt file 
that lists the Python modules required by the script. First, the script file obtains the URL of the review page of the specified business 
using firefox selenium, and then passes the URL to scrapy for scraping. For running the script, first you have install the requirements and then cd into 
the spiders folder in the terminal ( make sure to have scrapy installed ) and then run the following script: 

scrapy crawl google -o reviews.csv -a bname="aspria berlin ku'damm". 

You can pass any business name for scripting in the "banme" argument. 

