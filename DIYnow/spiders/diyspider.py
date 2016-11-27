# https://blog.siliconstraits.vn/building-web-crawler-scrapy/

# makezine sitemap http://makezine.com/sitemap/
# instructables sitemap http://www.instructables.com/sitemap/instructables/
#
# TODO
# Exclude education category from makezine searches
# Exclude maker news category from makezine searches
# Exclude uncategorized category from makezine searches?
# Check if site has not chnaged its format, if no proceed, if yes use backup site
# 	(if no snippet returned, use different site)

from scrapy.spiders import Spider
from DIYnow.items import DiynowItem
from scrapy.http import Request
import random

NUM_MAKEZINE_PROJECTS = 3

class MakezineSpider(Spider):
	# name of the spider, used to launch the spider
	name = "Makezine"

	# a list of URLs that the crawler will start at
	start_urls = ["http://makezine.com/sitemap/"]

	def parse(self, response):
		# list of html elements with this xpath (the project categories)
		categories = response.xpath('//li[contains(@class, "title")]/a')

		# ensure this list is not empty (site format is same)
		if categories.extract_first() is not None:

			for i in range(NUM_MAKEZINE_PROJECTS):
				# join our current url with the next category
				category = response.urljoin(
					# get a list of project cateogry htmls from the sitemap
					(categories.xpath('@href').extract())
					# choose random project category html from list
					[random.randrange(0, len(categories))])

				yield Request(category, callback = self.parse_makezine_projects)

	def parse_makezine_projects(self, response):

		# list of html elements with xpath that leads to project link
		projects = response.xpath('//ul[contains(@class, "sitemap_links")]/li/a')

		# declare instance of a DiynowItem, fill in its fields, then yield
		item = DiynowItem()
		process_info(projects, item)
		yield item

def process_info(projects, item):
	# chose a random number between 0 and the number of projects in projects
	rand_num = random.randrange(0, len(projects))

	# get the title and html info out of that random number project
	item["title"] = (projects.xpath('text()').extract())[rand_num]
	item["html"] = (projects.xpath('@href').extract())[rand_num]

