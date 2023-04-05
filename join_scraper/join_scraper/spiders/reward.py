import scrapy
import json
import re
from datetime import datetime
from ..items import AwardItem
import math


class RewardSpider(scrapy.Spider):
    name = 'reward_spider'
    custom_settings = {
        "CONCURRENT_REQUESTS": 8
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories_url = 'https://rewardsforjustice.net/wp-json/wp/v2/crime-category'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                          '(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        self.default_val = "null"

    def start_requests(self):
        """
        First request to all the categories.
        """
        yield scrapy.Request(self.categories_url, callback=self.parse_categories,
                             headers={
                                 'User-Agent': self.user_agent
                             })

    def parse_categories(self, response):
        """
        Parse all the categories and forward req to persons Endpoint.
        """
        data = json.loads(response.body)

        for categ in data:
            category = categ['name']
            categ_id = categ['id']

            # Count of all items for a category and divide it by numbers of items per page,
            # round it up to higher number so we don't miss any page.
            count = categ['count']
            pages = math.ceil(count / 9)

            # Iterate through all pages of a category
            for page in range(1, pages + 1):
                yield scrapy.Request(f'https://rewardsforjustice.net/wp-json/wp/v2/rewards?crime-category={categ_id}&page={page}',
                                     callback=self.parse_persons_urls, cb_kwargs={"category": category})

    def parse_persons_urls(self, response, category):
        """
        Parse the website link for all the persons on the page and forward req to parse each person.
        """
        data = json.loads(response.body)

        for person in data:
            url = person['link']
            yield scrapy.Request(url, callback=self.parse_person,
                                 headers={
                                     'User-Agent': self.user_agent,
                                     'Accept': "*/*",
                                     'Accept-Encoding': 'gzip, deflate, br',
                                     'Connection': 'keep-alive'
                                 },
                                 cb_kwargs={"category": category})

    def parse_person(self, response, category):
        """
        Parse each field for the person, set it in the item object and yield it.
        """
        url = response.url
        category_name = category
        title = response.css('div[data-id="f2eae65"] > div > h2::text').get()

        reward_amount_re = re.findall(r"(\d+) million", response.css('div[data-id="5e60756"] > div > h2::text').get()) \
            if response.css('div[data-id="5e60756"] > div > h2::text') else self.default_val
        reward_amount = self.default_val
        if reward_amount != "null":
            reward_amount = f"${reward_amount_re[0]} million"

        associated_org = response.css('div[data-id="095ca34"] > div > p > a::text').get() \
            if response.css('div[data-id="095ca34"] > div > p > a::text') else self.default_val
        associated_loc = " ".join(response.css('div[data-id="0fa6be9"] > div > div > span::text').getall()) \
            if response.css('div[data-id="0fa6be9"] > div > div > span::text') else self.default_val

        about = response.css('div[data-id="52b1d20"] > div > p::text').get() \
            if response.css('div[data-id="52b1d20"] > div > p::text') else self.default_val
        images = ", ".join(response.css('div[id="gallery-1"] > figure > div > a::attr(href)').getall()) \
            if response.css('div[id="gallery-1"] > figure > div > a::attr(href)') else self.default_val

        date_of_birth = response.css('div[data-id="9a896ea"] > div::text').get().strip() \
            if response.css('div[data-id="9a896ea"] > div::text') else self.default_val
        date_of_birth_iso = self.format_date(date_of_birth)

        # Set person item object
        person = AwardItem(page_url=url,
                           category=category_name,
                           title=title,
                           reward_amount=reward_amount,
                           associated_organizations=associated_org,
                           associated_locations=associated_loc,
                           about=about,
                           image_urls=images,
                           date_of_birth=date_of_birth_iso)

        yield person

    def format_date(self, date: str) -> str:
        """
        Method to format the date into ISO format.
        """
        date_lst = []
        if ";" in date:
            date_s = date.split(";")
            for d in date_s:
                d = d.strip()
                if re.search(r"(\w+) (\d+), (\d+)", d, re.I):
                    iso_date = datetime.strptime(d, "%B %d, %Y").strftime("%Y-%m-%d")
                    date_lst.append(iso_date)
                else:
                    date_lst.append(d)
        else:
            try:
                date_lst.append(datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d"))
            except ValueError:
                date_lst.append(date)
        return "; ".join(date_lst)
