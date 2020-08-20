import scrapy
from crawler.items import WgItem
from scrapy.shell import inspect_response

class WG_Spider(scrapy.Spider):
    name = 'wg_spider'
    start_urls = ['https://www.wg-gesucht.de/wg-zimmer-in-Nurnberg.96.0.1.0.html#']

    def parse(self, response):
        # focus to main content of the cards on the website
        main_content = response.xpath('//div[@class="wgg_card offer_list_item "]//' +
                                        'div[contains(@class,"card_body")]')
        
        # extract the info of the shown cards
        title_list = main_content.xpath('normalize-space(.//div/h3/a/text())').extract() 
        link_list = main_content.xpath('.//div/h3/a/@href').extract()
        undertitle_list = main_content.xpath('normalize-space(.//div[@class="col-xs-11"]' + 
                                                              '//span[1])').extract()
        price_list = main_content.xpath('.//div[@class="row noprint middle"]' +
                                          '/div[1]/b/text()').extract()
        timespan_list = main_content.xpath('normalize-space(.//div[@class="row noprint middle"]'+                                                            '/div[2]/text())').extract()
        squaremeter_list = main_content.xpath('.//div[@class="row noprint middle"]' +
                                                '/div[3]/b/text()').extract()
        
        # iterate through all lists and store every entry as item 
        for title, link, undertitle, price, timespan, squaremeter in zip(title_list, link_list,
                                                                         undertitle_list, 
                                                                         price_list,
                                                                         timespan_list,
                                                                         squaremeter_list): 
            # store the information in item
            wg_item = WgItem()
            wg_item['title'] = title
            wg_item['link'] = link
            wg_item['undertitle'] = undertitle
            wg_item['price'] = price
            wg_item['timespan'] = timespan
            wg_item['squaremeter'] = squaremeter

            yield wg_item
