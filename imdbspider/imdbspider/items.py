import scrapy


class ImdbspiderItem(scrapy.Item):

    id = scrapy.Field()
    title = scrapy.Field()
    poster = scrapy.Field()
    genres = scrapy.Field()
    plot = scrapy.Field()
    score = scrapy.Field()
    num_votes = scrapy.Field()
    director = scrapy.Field()
    release_date = scrapy.Field()
    countries = scrapy.Field()
    languages = scrapy.Field()
    aka = scrapy.Field()
    keywords = scrapy.Field()
    cast_character = scrapy.Field()
    quotes = scrapy.Field()

