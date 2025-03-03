import scrapy
import os
import pandas as pd
from imdbspider.items import ImdbspiderItem


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["imdb.com"]
    # xxxx will be replaced by the specific year when scraping
    df = pd.read_csv("xxxx_urls.tsv", sep="\t")
    if os.path.exists('processed_url.tsv'):
        df_processed = pd.read_csv("processed_url.tsv", sep="\t")
        p_urls = set(df_processed["url"].tolist())
        total_urls = set(df["imdb_url"].tolist())
        start_urls = list(total_urls - p_urls)
    else:
        start_urls = set(df["imdb_url"].tolist())


    def parse(self, response,  **kwargs):
        item = ImdbspiderItem()
        item['id'] = response.url.split("/")[-2]
        item['title'] = response.xpath("//h1[@data-testid='hero__pageTitle']/span/text()").get()
        item['poster'] = response.xpath('//meta[@property="og:image"]/@content').get()
        item['genres'] = response.xpath('//div[@data-testid="interests"]//div[@class="ipc-chip-list__scroller"]//span/text()').getall()

        item['plot'] = response.xpath('//p[@data-testid="plot"]//span[@data-testid="plot-xl"]/text()').get()

        item['score'] = response.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]//span[1]/text()').get()
        item['num_votes'] = response.xpath('//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/following-sibling::div[2]/text()').get()

        item['director'] = response.xpath('//section[@data-testid="hero-parent"]//li[@data-testid="title-pc-principal-credit"][1]//li/a/text()').get()


        item['release_date'] = response.xpath('//li[@data-testid="title-details-releasedate"]/div//a/text()').get()
        item['countries'] = response.xpath('//li[@data-testid="title-details-origin"]/div//a/text()').getall()
        item['languages'] = response.xpath('//li[@data-testid="title-details-languages"]/div//a/text()').getall()
        item['aka'] = response.xpath('//li[@data-testid="title-details-akas"]/div//span/text()').get()
        yield scrapy.Request(response.url + 'keywords/',
                             meta={'main_url': response.url,'item':item},
                             callback=self.parse_keywords)

    def parse_keywords(self, response):
        main_url = response.request.meta['main_url']
        item = response.request.meta['item']
        item['keywords'] = response.xpath('//li[@data-testid="list-summary-item"]//a[1]/text()').getall()
        yield scrapy.Request(main_url + 'fullcredits/cast/',
                             meta={'main_url': main_url,'item':item},
                             callback=self.parse_cast)

    def parse_cast(self, response):
        main_url = response.request.meta['main_url']
        item = response.request.meta['item']

        if main_url.startswith("https://m.imdb.com/"):
            cast_data = response.xpath('//section[@id="fullcredits-content"]//h4/text()').getall()
            character_data = response.xpath('//section[@id="fullcredits-content"]//p/text()').getall()
            cast_character = dict(zip(cast_data, character_data))
            item['cast_character'] = cast_character

        elif main_url.startswith("https://www.imdb.com/"):
            cast_data = response.xpath('//table[@class="cast_list"]//tr[@class="odd" or @class="even"]//td[2]/a/text()').getall()
            character_data = response.xpath('//table[@class="cast_list"]//td[@class="character"]/a//text()').getall()
            character_data += [" "] * (len(cast_data) - len(character_data))
            cast_character = dict(zip(cast_data, character_data))
            item['cast_character'] = cast_character
        yield scrapy.Request(main_url + 'quotes/',
                             meta={'main_url': main_url, 'item': item},
                             callback=self.parse_quotes)
    def parse_quotes(self, response):
        main_url = response.request.meta['main_url']
        item = response.request.meta['item']
        item['quotes'] = response.xpath('string(//div[@class="ipc-html-content-inner-div"][1])').get()
        yield scrapy.Request(main_url + 'plotsummary/',
                             meta={'main_url': main_url, 'item': item},
                             callback=self.parse_plot)

    def parse_plot(self, response):
        item = response.request.meta['item']
        item['plot'] = response.xpath('//div[@data-testid="sub-section-summaries"]//ul/li[1]//div[@class="ipc-html-content-inner-div" and @role="presentation"]/text()').get()
        yield item



















        
