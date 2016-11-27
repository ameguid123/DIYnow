# https://blog.siliconstraits.vn/building-web-crawler-scrapy/

# makezine sitemap http://makezine.com/sitemap/
# instructables sitemap http://www.instructables.com/sitemap/instructables/

from scrapy.spiders import Spider
from DIYnow.items import DiynowItem
from scrapy.http import Request
import random

class TitlesSpider(Spider):
	# name of the spider, used to launch the spider
	name = "titles"

	# allowed_domains = "makezine.com"

	# a list of URLs that the crawler will start at
	start_urls = ["https://makezine.com/sitemap/"]

	# start_urls = [
		# "https://www.instructables.com/",
	#	"https://makezine.com/projects/"
	#	]
	#for url in urls:
	#	yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		# list of html elements with this xpath (the project categories)
		categories = response.xpath('//li[contains(@class, "title")]/a')
		# the html of our first random project cateogry
		cat1 = "https://makezine.com/sitemap/" + str(
			# get a list of project cateogry htmls from the sitemap
			(categories.xpath('@href').extract())
			# choose random project category html from list
			[random.randrange(0, len(categories))])
		#yield Request(cat1, self.parse)
		#item = DiynowItem()
		#process_info(cat1, item)
		#yield item


def process_info(info, item):
	#item["title"] = info.xpath('text()').extract()
	item["html"] = info#.xpath('@href').extract()


