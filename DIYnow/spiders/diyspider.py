from scrapy.spiders import Spider
from DIYnow.items import DiynowItem
from scrapy.http import Request

class TitlesSpider(Spider):
	name = "titles"
	# allowed_domains = "makezine.com"
	start_urls = ["https://makezine.com/projects/"]
	# start_urls = [
		# "https://www.instructables.com/",
	#	"https://makezine.com/projects/"
	#	]
	#for url in urls:
	#	yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		titles = response.xpath('//*[@itemprop ]/a/text()').extract() #/text()

		for title in titles:
			item = DiynowItem()
			item["title"] = title
			yield item
