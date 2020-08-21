import re
import scrapy
from datetime import datetime, timedelta
from crawler.items import WgItem
from scrapy.shell import inspect_response

class WG_Spider(scrapy.Spider):
    name = 'wg_spider'
    start_urls = ['https://www.wg-gesucht.de/wg-zimmer-in-Nurnberg.96.0.1.0.html?' +
                  'category=0&city_id=96&rent_type=0&noDeact=1&sMin=10&img=1&rent_types%5B0%5D=0']

    def __init__(self):
        self.counter = 0
        self.DATE_REGEX = '[0-9]{2}\.[0-9]{2}\.[0-9]{4}'

    def parse(self, response):
        # focus to main content of the cards on the website
        main_content = response.xpath('//div[@class="wgg_card offer_list_item "]//' +
                                        'div[contains(@class,"card_body")]')
        # if current page has content
        if len(main_content)>1:
            # extract the info of the shown cards
            title_list = main_content.xpath('normalize-space(.//div/h3/a/text())').extract()
            link_list = main_content.xpath('.//div/h3/a/@href').extract()
            undertitle_list = main_content.xpath('normalize-space(.//div[@class="col-xs-11"]' +
                                                                  '//span[1])').extract()
            price_list = main_content.xpath('.//div[@class="row noprint middle"]' +
                                              '/div[1]/b/text()').extract()
            timespan_list = main_content.xpath('normalize-space(.//div[@class="row noprint middle"]'+
                                                                '/div[2]/text())').extract()
            squaremeter_list = main_content.xpath('.//div[@class="row noprint middle"]' +
                                                   '/div[3]/b/text()').extract()

            # iterate through all lists and store every entry as item 
            for title, link, undertitle, price, timespan, squaremeter in zip(title_list, link_list,
                                                                             undertitle_list,
                                                                             price_list,
                                                                             timespan_list,
                                                                             squaremeter_list):
                # extract the dates from the timespan variable (e.g. 01.10.2020 - 30.02.2021)
                date_list = re.findall(self.DATE_REGEX, timespan)
                # convert to dates
                date_list = [datetime.strptime(date, '%d.%m.%Y') for date in date_list]
                # if there is a actual timespan (most posts just have start time)
                if len(date_list) == 2:
                    # get month diff between end and start; timespan the flat is rented out
                    num_months = (date_list[1].year - date_list[0].year)*12 + (date_list[1].month - date_list[0].month)
                    # set a threshold for the timespan
                    if num_months > 3 and num_months < 7:
                        # store the information in item
                        wg_item = WgItem()
                        wg_item['title'] = title
                        wg_item['link'] = link
                        wg_item['undertitle'] = undertitle
                        wg_item['price'] = price
                        wg_item['timespan'] = timespan
                        wg_item['squaremeter'] = squaremeter
                        # yield single wg
                        yield wg_item

            # set request for the next page
            url = re.sub('[0-9]+\.html',f'{self.counter}.html',response.url)
            self.counter += 1
            request = scrapy.Request(url=url, callback=self.parse, headers={'referer_url':response.url})
            # yield request
            yield request
