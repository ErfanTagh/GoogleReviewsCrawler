import scrapy
from scrapy.http.request import Request
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class GoogleSpider(scrapy.Spider):
    name = 'google'

    HEADERS = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66",
        'referer': None
    }

    def __init__(self, bname=None, *args, **kwargs):
        super(GoogleSpider, self).__init__(*args, **kwargs)
        print(bname)
        self.get_review_page_url(bname)
        self.start_requests()

    def get_review_page_url(self, bname):
        driver = webdriver.Firefox()
        driver.get("http://www.google.com")
        #
        elem_zero = driver.find_element(By.CSS_SELECTOR, "#L2AGLb > div:nth-child(1)")
        elem_zero.click()

        elem = driver.find_element(By.CLASS_NAME, "gLFyf")
        elem.clear()
        elem.send_keys(bname)
        elem.send_keys(Keys.RETURN)

        time.sleep(5)
        #
        elem_link = driver.find_element(By.XPATH,
                                        '/html/body/div[7]/div/div[11]/div[2]/div/div/div[2]/div/div[1]/div[2]/div[2]/div/div/span[3]/span/a/span')

        elem_link.click()
        #
        time.sleep(5)

        self.urls = []

        self.urls.append(driver.current_url)
        driver.close()

    def start_requests(self):

        for url in self.urls:
            async_id = url.split("lrd=")[1].split(",")[0]
            ajax_url = "https://www.google.com/async/reviewDialog?async=feature_id:" + str(
                async_id) + ",start_index:0,_fmt:pc,sort_by:newestFirst"
            yield Request(url=ajax_url, headers=self.HEADERS, callback=self.get_total_iteration)

    def get_total_iteration(self, response):
        total_reviews_text = response.css('.z5jxId::text').extract_first()
        total_reviews = int(re.sub(r'[^0-9]', '', total_reviews_text))

        temp = total_reviews / 10  # since
        new_num = int(temp)
        if temp > new_num:
            new_num += 1
        iteration_number = new_num

        j = 0
        print(iteration_number)
        if total_reviews > 10:
            for _ in range(0, iteration_number + 1):
                yield Request(url=response.request.url.replace('start_index:0', f'start_index:{j}'),
                              headers=self.HEADERS, callback=self.parse_reviews, dont_filter=True)
                j += 10
        else:
            yield Request(url=response.request.url, headers=self.HEADERS, callback=self.parse_reviews, dont_filter=True)

    def parse_reviews(self, response):

        all_reviews = response.xpath('//*[@id="reviewSort"]/div/div[2]/div')

        for review in all_reviews:
            reviewer = review.css('div.TSUbDb a::text').extract_first()
            description = review.xpath('.//span[@class="review-full-text"]/text()').extract_first()
            if description is None:
                description = review.css('.Jtu6Td span::text').extract_first()

                if description is None:
                    description = ''

            review_rating = review.xpath('.//span[@class="pjemBf"]/text()').extract_first()
            if review_rating is None:
                review_rating = review.xpath('.//span[@class="Fam1ne EBe2gf"]/@aria-label').extract_first()
                match = re.search(r'\d+', review_rating)

                if match:
                    # 👇️ First number found: 12
                    review_rating = match.group()
            else:
                review_rating = review_rating.split('/')[0]

            if review_rating.count(',') > 0:
                review_rating = review_rating.replace(',', '.')

            review_rating = float(review_rating)

            review_date = review.xpath('.//span[@class="dehysf lTi8oc"]/text()').extract_first()
            if review_date is None:
                review_date = review.xpath('.//span[@class="Qhbkge"]/text()').extract_first()

            owner_comment = review.xpath('.//div[@class="lororc"]/span/text()').extract_first()

            if owner_comment is not None:
                has_owner_review = True
            else:
                has_owner_review = False

            yield {
                "reviewer": reviewer,
                "description": description,
                "rating": review_rating,
                "review_date": review_date,
                "has_owner_review": has_owner_review,
                "owner_comment": owner_comment
            }
