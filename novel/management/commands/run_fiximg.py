import operator
import time
from functools import reduce

# from webdriver_manager.chrome import ChromeDriverManager
from django.core.management.base import BaseCommand
from django.db.models import Q
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from django_cms import settings
from django_cms.utils.cache_manager import CacheManager
from novel.models import NovelChapter, NovelSetting


class SeleniumScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # self.driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
        # self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(settings.SELENIUM_CHROME_DRIVE, chrome_options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def get_pages(self, by_selector="div.page-chapter"):
        """Get the line number of last company loaded into the list of companies."""
        # return self.driver.find_element_by_css_selector("div.reading-detail > div:last-child").get_attribute(by)
        return self.driver.find_elements_by_css_selector(by_selector)

    def get_links(self, url, timeout=3, page_by_selector="div.page-chapter", show_log=False):
        """Extracts and returns company links (maximum number of company links for return is provided)."""
        if show_log:
            print('[get_links] starting...')
        init_time = time.time()
        self.driver.get(url)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, page_by_selector)))

        if show_log:
            print('[get_links] get pages')
        pages = self.get_pages(page_by_selector)

        # store all initial src before scroll it
        initial_sources = []
        for page in pages:
            initial_images = page.find_elements_by_tag_name("img")
            for img in initial_images:
                initial_sources.append(img.get_attribute("src"))
        if not initial_sources:
            return []

        if show_log:
            print('[get_links] %s pages fetched' % len(pages))

        new_img = []
        for idx, page in enumerate(pages):
            start_time = time.time()
            if idx % 2 == 0 or idx == len(pages) - 1:
                self.driver.execute_script("return arguments[0].scrollIntoView(true);", page)

            img = page.find_element_by_tag_name("img")
            self.wait.until(lambda driver: img.get_attribute("src") != initial_sources[idx]
                                           or time.time() > start_time + timeout)
            new_img.append(img.get_attribute("src"))

        end_time = time.time() - init_time
        if show_log:
            print('[get_links] new images %s' % new_img)
            print('[get_links] total time %s' % end_time)
        # return [img_link.get_attribute("src")
        #         for img_link in self.driver.find_elements_by_css_selector(page_by_selector + " > img")]
        return new_img


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print('[Selenium Scraper] Starting...')
        scraper = SeleniumScraper()
        novel_setting = CacheManager(NovelSetting).get_from_cache()
        img_ignoring = []
        if novel_setting and novel_setting.img_ignoring:
            img_ignoring = novel_setting.img_ignoring.split(",")
        if not img_ignoring:
            return
        print('[Selenium Scraper] Query chapters...')
        query = reduce(operator.and_, (Q(images_content__icontains=item) for item in img_ignoring))
        chapters = NovelChapter.objects.filter(query)
        if not chapters:
            print('[Selenium Scraper] No chapter is invalid')
            return
        for chapter in chapters:
            print('[Selenium Scraper] Update images content for Chapter ID: ', chapter.id, ' - Chapter Name: ',
                  chapter.name)
            # url = 'http://www.nettruyen.com/truyen-tranh/trai-tim-sat/chap-12/678622'
            links = scraper.get_links(url=chapter.src_url, timeout=settings.SELENIUM_LAZY_LOADING_TIMEOUT,
                                      page_by_selector="div.page-chapter")
            chapter.images_content = '\n'.join(links)
            chapter.save()
        print('[Selenium Scraper] Finish')
