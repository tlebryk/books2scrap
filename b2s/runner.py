from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# dumps csv in "/data/___.csv"
if __name__ == "__main__":

    process = CrawlerProcess(get_project_settings())
    process.crawl("theme")
    process.crawl("list")
    process.start()
