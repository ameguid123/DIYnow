# https://blog.siliconstraits.vn/building-web-crawler-scrapy/

# makezine sitemap http://makezine.com/sitemap/
# instructables sitemap http://www.instructables.com/sitemap/instructables/
#
#

from scrapy.spiders import Spider
from DIYnow.items import DiynowItem
from scrapy.http import Request
import random

class TitlesSpider(Spider):
	# name of the spider, used to launch the spider
	name = "titles"

	# allowed_domains = "makezine.com"

	# a list of URLs that the crawler will start at
	start_urls = ["http://makezine.com/sitemap/"]

	# start_urls = [
	# "https://www.instructables.com/",
	#"https://makezine.com/projects/"
	#]
	#for url in urls:
	#yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		# list of html elements with this xpath (the project categories)
		categories = response.xpath('//li[contains(@class, "title")]/a')
		if categories.extract_first() is not None:
			# join our current url with the next category
			cat1 = response.urljoin(
				# get a list of project cateogry htmls from the sitemap
				(categories.xpath('@href').extract())
				# choose random project category html from list
				[random.randrange(0, len(categories))])

			yield Request(cat1, callback = self.parse_makezine_projects)
			#
			# fixing redirect
			# http://stackoverflow.com/questions/22795416/how-to-handle-302-redirect-in-scrapy
			#yield Request(cat1, meta = {
            #      'dont_redirect': True,
            #      'handle_httpstatus_list': [301]
            #  },callback = self.parse_makezine_projects)

	def parse_makezine_projects(self, response):
		item = DiynowItem()

		# list of html elements with xpath that leads to project link
		projects = response.xpath('//ul[contains(@class, "sitemap_links")]/li/a')

		item = DiynowItem()
		process_info(projects, item)
		yield item



def process_info(projects, item):
	# chose a random number between 0 and the number of projects in projects
	rand_num = random.randrange(0, len(projects))

	# get the title and html info out of that random number project
	item["title"] = (projects.xpath('text()').extract())[rand_num]
	item["html"] = (projects.xpath('@href').extract())[rand_num]

