# NOTE: currently writes csvs in utf-8 format
# This will read fine upon reading from the file using
# python file-io or pandas, but default excel is ISO-8859-1

import scrapy
import re

class ThemeSpider(scrapy.Spider):
    name = "theme"
    start_urls = ["http://books.toscrape.com/index.html"]
    nummap = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    custom_settings = {
        "ITEM_PIPELINES": {"b2s.pipelines.ThemePipeline": 400},
        "FEEDS": {
            r".\data\theme.csv": {
                "format": "csv",
                "encoding": "utf8",
                "overwrite": True,
                "fields": [
                    "Theme", 
                    "Number of Books", 
                    "Average Rating", 
                ],
            }
        },
    }

    def parse(self, response):
        themes = response.css("ul.nav.nav-list a")
        for el in themes:
            url = el.xpath(".//@href").get()
            theme = el.xpath(".//text()").get().strip()
            if theme == "Add a comment":
                continue
            theme_d = {"Theme": theme, "Number of Books": 0, "Ratings": []}
            yield response.follow(
                url,
                callback=self.themeparse,
                cb_kwargs=dict(theme_d=theme_d),
            )

    # returns total number of books and list of ratings
    def themeparse(self, response, theme_d):
        books = response.css("article.product_pod")
        for book in books:
            theme_d["Number of Books"] += 1
            theme_d["Ratings"].append(self.get_rating(book))
        nxt = response.css("li.next a::attr(href)").get()
        if nxt:
            yield response.follow(
                nxt, callback=self.themeparse, cb_kwargs=dict(theme_d=theme_d)
            )
        else:
            yield theme_d

    # comes in format "star-rating Two"
    def get_rating(self, book):
        rating = book.css("p.star-rating").xpath("@class").get().lower()
        rating = rating.split()[-1]
        return self.nummap[rating]


class ListSpider(scrapy.Spider):
    name = "list"
    nummap = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    start_urls = ["http://books.toscrape.com/index.html"]

    custom_settings = {
        "FEEDS": {
            r".\data\list.csv": {
                "format": "csv", 
                "encoding": "utf8", 
                "fields": [
                    "Title", 
                    "Rating", 
                    "Price", 
                    "Number Available", 
                    "Product Discription",
                ],
                "overwrite": True,
            }
        }
    }

    def parse(self, response):
        arts = response.css("article.product_pod")
        for art in arts:
            url = art.xpath(".//h3/a/@href").get()
            yield response.follow(url, callback=self.artparse)
        nxt = response.css("li.next a::attr(href)").get()
        if nxt:
            yield response.follow(nxt, callback=self.parse)

    def artparse(self, response):
        art_dict = {}
        # strip pound sign
        art_dict["Price"] = response.css("p.price_color::text").get()[1:]
        art_dict["Title"] = response.css("h1::text").get()
        # product description in p tag after "product description" div
        art_dict["Product Discription"] = response.xpath(
            "//div[@id='product_description']/following-sibling::p/text()"
        ).get()
        art_dict["Rating"] = self.get_rating(response)
        # get rid of \n padding
        x = "".join(response.css("p.instock::text").getall()).strip()
        # get digits
        art_dict["Number Available"] = re.search(r"\d+", x).group(0)
        return art_dict

    def get_rating(self, book):
        rating = book.css("p.star-rating").xpath("@class").get().lower()
        rating = rating.split()[-1]
        return self.nummap[rating]
