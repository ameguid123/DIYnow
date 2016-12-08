# https://blog.siliconstraits.vn/building-web-crawler-scrapy/

# makezine sitemap http://makezine.com/sitemap/
# instructables sitemap http://www.instructables.com/sitemap/instructables/
#
# TODO
# Exclude education category from makezine searches
# Exclude maker news category from makezine searches
# Exclude uncategorized category from makezine searches?
# Check if site has not chnaged its format, if no proceed, if yes use backup site
#   (if no snippet returned, use different site)

# implement item pipeline/get images?
# yield vs return
# # Try better xpaths for speed? no //'s, exact path? (less flexible...)

# http://stackoverflow.com/questions/11128596/scrapy-crawlspider-how-to-access-item-across-different-levels-of-parsing
from scrapy.spiders import Spider
from DIYnow.items import DiynowItem
from scrapy.http import Request
import random

NUM_MAKEZINE_PROJECTS = 3
NUM_INSTRUCTABLES_PROJECTS = 3
NUM_LIFEHACKER_PROJECTS = 3

# number of recent lifehacker DIY projects to reference (here last 5000)
LIFEHACKER_RANGE = 5000

# defines for project categories we exclude in Makezine search
MAKEZINE_EDUCATION = 3
MAKER_NEWS = 5
UNCATEGORIZED = 8
PAGE = 10

class ProjectSpider(Spider):
    # name of the spider, used to launch the spider
    name = "Projects"

    # a list of URLs that the crawler will start at
    start_urls = ["http://makezine.com/sitemap/"]

    # starting the chain of requests
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

            # http://stackoverflow.com/questions/17560575/using-scrapy-to-extract-information-from-different-sites
            # passing request to next site, instructables
            yield Request(url="http://www.instructables.com/sitemap/instructables/", callback=self.parse_instructables_categories)


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

    def parse_instructables_categories(self, response):
        # like parse_makezine_projects, with different xpath and restrictions
        categories = response.xpath('//ul[contains(@class, "main-listing")]/li/a')
        # ensure this list is not empty (site format is same)
        if categories.extract_first() is not None:

            for i in range(NUM_INSTRUCTABLES_PROJECTS):

                # join our current url with the next random category
                category = response.urljoin(
                    # get a list of project cateogry urls from the sitemap
                    (categories.xpath('@href').extract())
                    # choose random project category url from list
                    [random.randrange(0, len(categories))])

                # dont filter set to true to allow spider to crawl same category twice
                yield Request(category, callback = self.parse_instructables_projects, dont_filter = True)

            # passing request to next site at a random diy category page
            rand_num = random.randrange(0, LIFEHACKER_RANGE)
            yield Request(url="http://lifehacker.com/tag/diy?startIndex=" + str(rand_num), callback=self.parse_lifehacker_projects)


    def parse_instructables_projects(self, response):
        # list of html elements with xpath that leads to project link
        projects = response.xpath('//ul[contains(@class, "main-listing")]/li/a')

        # declare instance of a DiynowItem and start to fill in fields
        item = DiynowItem()
        process_info(projects, item)
        # find the url for the page of the random project of "item"
        project_page = response.urljoin(item["url"])

        # parse that random project page, and update item's image_url field
        request = Request(project_page, callback = self.parse_project_page, dont_filter = True)
        request.meta["item"] = item

        return request

    def parse_lifehacker_projects(self, response):
        # list of html elements with xpath that leads to project link
        projects = response.xpath('//h1[contains(@class, "headline entry-title js_entry-title")]/a')

        if projects.extract_first() is not None:
            for i in range(NUM_LIFEHACKER_PROJECTS):
                # declare instance of a DiynowItem and start to fill in fields
                item = DiynowItem()
                process_info(projects, item)

                # find the url for the page of the random project of "item"
                project_page = response.urljoin(item["url"])

                # parse that random project page, and update item's image_url field
                request = Request(project_page, callback = self.parse_project_page, dont_filter = True)
                request.meta["item"] = item

                yield request

    def parse_project_page(self, response):
        # getting our previously declared item by using metadata, per:
        # https://media.readthedocs.org/pdf/scrapy/1.0/scrapy.pdf, section 3.9 requests and responses
        item = response.meta["item"]
        # https://tech.shareaholic.com/2012/11/02/how-to-find-the-image-that-best-respresents-a-web-page/
        # look for og:image as the image that best represents the project
        image = response.xpath('//meta[@property="og:image"]')
        item["image_url"] = image.xpath('@content').extract_first()
        yield item

class SearchSpider(Spider):
    # name of the spider, used to launch the spider
    name = "Search"

    def __init__(self, *args, **kwargs):
        super(SearchSpider, self).__init__(*args, **kwargs)
        # http://stackoverflow.com/questions/15611605/how-to-pass-a-user-defined-argument-in-scrapy-spider
        # http://stackoverflow.com/questions/9681114/how-to-give-url-to-scrapy-for-crawling
        self.category = kwargs.get("category")
        self.start_urls = ["http://www.makezine.com/page/1/?s=%s" % kwargs.get("category")]

    # starting the chain of requests
    def parse(self, response):
        # list of html elements with xpath that leads to project link
        projects = response.xpath('//div[contains(@class, "media-body")]/h2/a')

        # ensure this list is not empty (site format is same)
        if projects.extract_first() is not None:
            for i in range(NUM_MAKEZINE_PROJECTS):
                # declare instance of a DiynowItem and start to fill in fields
                item = DiynowItem()
                process_info(projects, item)
                # find the url for the page of the random project of "item"
                project_page = response.urljoin(item["url"])

                # parse that random project page, and update item's image_url field
                request = Request(project_page, callback = self.parse_project_page, dont_filter = True)
                request.meta["item"] = item

                yield request
            # http://stackoverflow.com/questions/17560575/using-scrapy-to-extract-information-from-different-sites
            # passing request to next site, instructables
            url = "http://www.instructables.com/howto/%s" % self.category
            yield Request( url=url, callback=self.parse_instructables_projects, dont_filter = True)

    def parse_instructables_projects(self, response):
        # list of html elements with xpath that leads to project link
        projects = response.xpath('//div[contains(@class, "cover-item")]/a')
        if projects.extract_first() is not None:
            for i in range(NUM_INSTRUCTABLES_PROJECTS):
                # declare instance of a DiynowItem and start to fill in fields
                # //div[contains(@class, "cover-item")]/a/@title
                item = DiynowItem()
                process_instructables_info(projects, item)
                # find the url for the page of the random project of "item"
                project_page = response.urljoin(item["url"])
                # the instructables search page requires a modified url
                item["url"] = project_page

                # parse that random project page, and update item's image_url field
                request = Request(project_page, callback = self.parse_project_page, dont_filter = True)
                request.meta["item"] = item

                yield request
        # http://stackoverflow.com/questions/17560575/using-scrapy-to-extract-information-from-different-sites
        # passing request to next site, instructables
        url = "https://lifehacker.com/search?q=%s" % self.category
        yield Request( url=url, callback=self.parse_lifehacker_projects, dont_filter = True)

    def parse_lifehacker_projects(self, response):
        # list of html elements with xpath that leads to project link
        projects = response.xpath('//h1[contains(@class, "headline entry-title js_entry-title")]/a')

        if projects.extract_first() is not None:
            for i in range(NUM_LIFEHACKER_PROJECTS):
                # declare instance of a DiynowItem and start to fill in fields
                item = DiynowItem()
                process_info(projects, item)

                # find the url for the page of the random project of "item"
                project_page = response.urljoin(item["url"])

                # parse that random project page, and update item's image_url field
                request = Request(project_page, callback = self.parse_project_page, dont_filter = True)
                request.meta["item"] = item

                yield request

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
    # this process could fail if formatted oddly, if so, get a different project
    try:
        item["title"] = (projects.xpath('text()').extract())[rand_num]
        item["url"] = (projects.xpath('@href').extract())[rand_num]
    except IndexError:
        process_info(projects, item)

# unfortunately instructables search page uses different xpath
def process_instructables_info(projects, item):
     # chose a random number between 0 and the number of projects in projects
    rand_num = random.randrange(0, len(projects))

    # get the title and url info out of that random number project
    # this process could fail if formatted oddly, if so, get a different project
    try:
        item["title"] = (projects.xpath('@title').extract())[rand_num]
        item["url"] = (projects.xpath('@href').extract())[rand_num]
    except IndexError:
        process_info(projects, item)

