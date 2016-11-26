# https://blog.siliconstraits.vn/building-web-crawler-scrapy/

# makezine sitemap http://makezine.com/sitemap/
# instructables sitemap http://www.instructables.com/sitemap/instructables/
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
		infos = response.xpath('//*[@itemprop ]/a')
		for info in infos:
			item = DiynowItem()
			item["title"] = info.xpath('text()').extract()
			item["html"] = info.xpath('@href').extract()
			yield item