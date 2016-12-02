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

# implement item pipeline/get images?
# yield vs return

from scrapy.spiders import Spider
from DIYnow.items import DiynowItem
from scrapy.http import Request
import random

NUM_MAKEZINE_PROJECTS = 3

# defines for project categories we exclude in Makezine search
MAKEZINE_EDUCATION = 3
MAKER_NEWS = 5
UNCATEGORIZED = 8
PAGE = 10

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
				# generate a random number to select a random project category
				# however, exclude certain categories, (not diy project related)
				rand_num = -1
				while(rand_num == -1 or rand_num == MAKEZINE_EDUCATION or
						rand_num == MAKER_NEWS or rand_num == UNCATEGORIZED or
						rand_num == PAGE):

					rand_num = random.randrange(0, len(categories))
				# join our current url with the next random category
				category = response.urljoin(
					# get a list of project cateogry urls from the sitemap
					(categories.xpath('@href').extract())
					# choose random project category url from list
					[rand_num])

				# dont filter set to true to allow spider to crawl same category twice
				yield Request(category, callback = self.parse_makezine_projects, dont_filter = True)

	def parse_makezine_projects(self, response):
		# list of html elements with xpath that leads to project link
		projects = response.xpath('//ul[contains(@class, "sitemap_links")]/li/a')

		# declare instance of a DiynowItem and start to fill in fields
		item = DiynowItem()
		process_info(projects, item)
		# find the url for the page of the random project of "item"
		project_page = response.urljoin(item["url"])

		# parse that random project page, and update item's image_url field
		request = Request(project_page, callback = self.parse_project_page, dont_filter = True)
		request.meta["item"] = item

		return request

	def parse_project_page(self, response):
		# getting our previously declared item by using metadata, per:
		# https://media.readthedocs.org/pdf/scrapy/1.0/scrapy.pdf, section 3.9 requests and responses
		item = response.meta["item"]
		# https://tech.shareaholic.com/2012/11/02/how-to-find-the-image-that-best-respresents-a-web-page/
		# look for og:image as the image that best represents the project
		image = response.xpath('//meta[@property="og:image"]')
		item["image_url"] = image.xpath('@content').extract_first()
		yield item

def process_info(projects, item):
	# chose a random number between 0 and the number of projects in projects
	rand_num = random.randrange(0, len(projects))

	# get the title and url info out of that random number project
	item["title"] = (projects.xpath('text()').extract())[rand_num]
	item["url"] = (projects.xpath('@href').extract())[rand_num]

