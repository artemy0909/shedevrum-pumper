import json
from random import randint, choice

from time import sleep

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver

from logger import Logger, LogLevel

class Client:

    def __init__(self):
        self.driver = webdriver.Edge()
        self.driver.implicitly_wait(10)
        # self.html = ""
        # self.all_data = []

    def run(self):
        # cookies_on_page = self.driver.get_cookies()
        # with open("cookie.json", "w") as file:
        #     json.dump(cookies_on_page, file)
        self.driver.get("https://shedevrum.ai/recent/")

        input(">вошел?")
        logger.to_log(0, "START")

        # with open('cookie.json', 'r') as file:
        #     cookies = json.load(file)
        # for e in cookies:
        #     self.driver.add_cookie(e)

        # self.driver.refresh()
        html = self.driver.find_element(By.TAG_NAME, 'html')

        parsed_elements = []
        subs = 0
        likes = 0
        while True:
            scroll_range = choice([6, 11, 16])
            for i in range(1, scroll_range):
                sleep_ms = randint(500, 1250)
                html.send_keys(Keys.SPACE)
                logger.to_log(1, "SCROLL", f"{i} out of {scroll_range}, wait {sleep_ms} ms")
                sleep(sleep_ms / 1000)
            all_elements = self.driver.find_elements(By.TAG_NAME, "article")
            for e in all_elements:
                if e not in parsed_elements:
                    try:
                        subscribe = e.find_element(By.TAG_NAME, 'button')
                        like = e.find_element(By.CSS_SELECTOR, 'div.font-bold.text-button')
                    except NoSuchElementException:
                        parsed_elements.append(e)
                        continue
                    if not like.text.isdigit() or int(like.text) > 50:
                        parsed_elements.append(e)
                        continue
                    self.driver.execute_script("arguments[0].click();", subscribe)
                    subs += 1
                    logger.to_log(3, "SUBSCRIBE", f"total subs - {subs}")
                    self.driver.execute_script("arguments[0].click();", like)
                    likes += 1
                    logger.to_log(3, "LIKE", f"total likes - {likes}",
                                  user_href=e.find_element(By.CLASS_NAME, 'shrink-0').get_attribute("href"))
                    parsed_elements.append(e)
                    sleep_ms = randint(8000, 12000)
                    logger.to_log(3, "SLEEP", f"wait {sleep_ms} ms")
                    sleep(sleep_ms / 1000)

    # def doom_scroller(self):
        

if __name__ == '__main__':
    logger = Logger()
    try:
        Client().run()
    except BaseException as error:
        logger.to_log(LogLevel.CRITICAl, "CRITICAL", error_args=error.args)
        error.with_traceback()
    logger.stop()

