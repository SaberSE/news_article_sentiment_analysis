"""
This will be the webscraper loaded into an AWS EC2 instance that will get news articles from
News websites.

Specifically: NYT, CNN, FOX, WSJ, The Guardian, and Washington Post
"""

import pymongo
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

class SeleniumUrls(object):

    def __init__(self, db_name, collection_name, site_name, uri = None):
        self.db_name = db_name
        self.collection_name = collection_name
        self.coll = self._launch_mongo(uri)
        self.site_name = site_name

    def _launch_mongo(self, uri = None):
        mc = pymongo.MongoClient(uri)
        db = mc.get_database(self.db_name)
        coll = db.get_collection(self.collection_name)

        return coll

    def get_urls_page_number(self, url_base, num_pages, class_name, tag , art_id = None, increments = None):
        """
        Launches Mongo instance and stores urls in collection within database
        Inputs: url_base: base url --> format, "www.-----/page={}".format(page_number)
                num_pages: number of pages wanted to scrape , currently about 10 per page so need ~1000 pages
                increments: some websites have both page number and increment if None provided, ignore
        Outputs: None
        """
        driver = webdriver.Chrome('/Users/npng/.ssh/chromedriver')
        for i in xrange(1, num_pages+1):
            page_number = i
            increment_ten = i*10
            article_urls = []
            driver.get(url_base.format(page_number))
            print "loaded page {}, waiting 2.5 seconds".format(i)
            time.sleep(2.5)
            urls = driver.find_elements_by_class_name(class_name)[0].find_elements_by_tag_name(tag)
            print len(urls)
            for url in urls:
                candidate_url = str(url.get_attribute('href'))
                if art_id:
                    if art_id in candidate_url.split('/'):
                        article_urls.append(candidate_url)
                else:
                    article_urls.append(candidate_url)

            self.coll.find_one_and_update({'site':self.site_name}, { '$addToSet':{'urls':{ '$each' : article_urls}}}, upsert = True)

            print "page {} done".format(i)
        driver.quit()

if __name__ == '__main__':
    page_number = 1
    increments_twenty = 0
    increment_ten = 0
    nyt = "https://query.nytimes.com/search/sitesearch/?action=click&contentCollection&region=TopBar&WT.nav=searchWidget&module=SearchSubmit&pgtype=Homepage#/politics/since1851/document_type%3A%22article%22/{}/allauthors/newest/"
    guardian = "https://www.theguardian.com/us-news/us-politics?page={}"
    wash_post = "https://www.washingtonpost.com/newssearch/?query=politics&sort=Date&datefilter=All%20Since%202005&contenttype=Article&spellcheck&startat={}#top".format(increments_twenty)
    wsj = "https://www.wsj.com/search/term.html?KEYWORDS=politics&min-date=2013/10/09&max-date=2017/10/09&page={}&isAdvanced=true&daysback=4y&andor=AND&sort=date-desc&source=wsjarticle"
    cnn = "http://www.cnn.com/search/?q=politics&size=10&page={}&type=article&from={}".format(page_number, increment_ten)
    fox = "http://www.foxnews.com/search-results/search?q=politics&ss=fn&sort=latest&start={}".format(increment_ten)


    #NYT --> element = searchResults, tag = a
    nyt_selenium = SeleniumUrls(db_name = 'news_articles', collection_name = 'urls', site_name = 'nyt')
    nyt_selenium.get_urls_page_number(nyt, 1000, 'searchResults', 'a')

    wsj_selenium = SeleniumUrls(db_name = 'news_articles', collection_name = 'urls', site_name = 'wsj')
    wsj_selenium.get_urls_page_number(wsj, 500, 'search-results-sector', 'a', art_id = 'articles')


    # driver = webdriver.Chrome('/Users/npng/.ssh/chromedriver')
    # driver.get("https://www.wsj.com/search/term.html?KEYWORDS=politics&min-date=2013/10/09&max-date=2017/10/09&page=1&isAdvanced=true&daysback=4y&andor=AND&sort=date-desc&source=wsjarticle")
    # urls = driver.find_elements_by_class_name('search-results-sector')[0].find_elements_by_tag_name('a')
    # article_urls = []
    # for url in urls:
    #     candidate_url = str(url.get_attribute('href'))
    #     if 'articles' in candidate_url.split('/'):
    #         article_urls.append(candidate_url)
    #
    #
    # article_urls


"""
bottom of page
"""
