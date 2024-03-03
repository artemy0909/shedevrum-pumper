import datetime
from random import randint

from time import sleep

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from logger import Logger, LogLevel


class Tracker:
    def __init__(self, max_likes=0, max_subs=0, target_secs_for_like=6, target_secs_for_sub=12, work_minutes=420):
        self.total_likes = 0
        self.total_subs = 0
        self.max_likes = max_likes
        self.max_subs = max_subs
        self.target_secs_for_like = target_secs_for_like
        self.target_secs_for_sub = target_secs_for_sub
        self.work_minutes = work_minutes
        self.start_time = datetime.datetime.now()

    def is_time_to_stop(self):
        return datetime.datetime.now() > self.start_time + datetime.timedelta(minutes=self.work_minutes)

    def action_avg(self, value):
        return round((datetime.datetime.now() - self.start_time).seconds / value)

    def secs_for_like(self):
        return self.action_avg(self.total_likes)

    def secs_for_sub(self):
        return self.action_avg(self.total_subs)

    def like(self):
        self.total_likes += 1

    def sub(self):
        self.total_subs += 1
        logger.to_log(3, "SUBSCRIBE", f"total subs - {self.total_subs}")


class BubbleObj:

    def __init__(self, element: WebElement):
        try:
            self.subscribe_button = element.find_element(By.TAG_NAME, 'button')
        except NoSuchElementException:
            self.subscribe_button = None
        try:
            self.like_button = element.find_element(By.CSS_SELECTOR, 'div.font-bold.text-button')
        except NoSuchElementException:
            self.like_button = None
        try:
            self.href = element.find_element(By.CLASS_NAME, 'shrink-0').get_attribute("href")
        except NoSuchElementException:
            self.href = None

    def like_action(self, driver):
        if self.like_button:
            driver.execute_script("arguments[0].click();", self.like_button)

    def sub_action(self, driver):
        driver.execute_script("arguments[0].click();", self.subscribe_button)


class Client:
    DEFAULT_SCROLL_RANGE = 5
    SHEDEVRUM_HOME_PAGE = "https://shedevrum.ai/"
    SHEDEVRUM_RECENT_PAGE = "https://shedevrum.ai/recent/"

    def __init__(self):
        self.driver = webdriver.Edge()
        self.driver.implicitly_wait(10)
        self.current_session: Tracker = None
        self.scroll_obj = None
        self.bubble_obj_conveyor: list[BubbleObj] = []
        self.parsed_elements = []
        # self.html = ""
        # self.all_data = []

    def run(self):
        # cookies_on_page = self.driver.get_cookies()
        # with open("cookie.json", "w") as file:
        #     json.dump(cookies_on_page, file)

        # with open('cookie.json', 'r') as file:
        #     cookies = json.load(file)
        # for e in cookies:
        #     self.driver.add_cookie(e)
        self.open_home_page()
        mode = ""
        while not mode.isdigit():
            mode = input("1. doom\n2. miner\n3. fisher\n4. lover\n>mode?")
        mode = int(mode)
        input(">login?")
        self.current_session = Tracker()
        if mode == 1:
            self.doom_mode()

    def open_home_page(self):
        self.driver.get(self.SHEDEVRUM_HOME_PAGE)

    def init_scroll(self):
        self.scroll_obj = self.driver.find_element(By.TAG_NAME, 'html')

    def scroll(self):
        for i in range(self.DEFAULT_SCROLL_RANGE):
            self.scroll_obj.send_keys(Keys.SPACE)
            sleep_ms = self.rand_scroll_sleep_time
            logger.to_log(1, "SCROLL", f"{i + 1} out of {self.DEFAULT_SCROLL_RANGE},"
                                       f" wait {self.rand_scroll_sleep_time} ms")
            sleep(sleep_ms / 1000)

    @property
    def rand_scroll_sleep_time(self):
        return randint(500, 1000)

    @property
    def rand_sub_sleep_time(self):
        return randint(5000, 10000)

    def scan_for_bubbles(self):
        all_elements = self.driver.find_elements(By.TAG_NAME, "article")
        for element in all_elements:
            if element not in self.parsed_elements:
                self.bubble_obj_conveyor.append(BubbleObj(element))

    def like(self, bubble: BubbleObj):
        bubble.like_action(self.driver)
        self.current_session.like()
        logger.to_log(3, "LIKE", f"total likes - {self.current_session.total_likes}", user_href=bubble.href)

    def sub(self, bubble: BubbleObj):
        bubble.sub_action(self.driver)
        self.current_session.sub()

    def sub_and_like_bubbles(self):
        while self.bubble_obj_conveyor:
            # self.sub(self.bubble_obj_conveyor[0])
            self.like(self.bubble_obj_conveyor[0])
            del self.bubble_obj_conveyor[0]
            sleep_ms = self.rand_sub_sleep_time
            logger.to_log(3, "SLEEP", f"wait {sleep_ms} ms")
            sleep(sleep_ms / 1000)

    def doom_mode(self):
        logger.to_log(0, "START", "doom mode")
        self.init_scroll()
        while not self.current_session.is_time_to_stop():
            self.scroll()
            self.scan_for_bubbles()
            self.sub_and_like_bubbles()
        logger.to_log(4, "STOP")


if __name__ == '__main__':
    logger = Logger()
    try:
        Client().run()
    except BaseException as error:
        logger.to_log(LogLevel.CRITICAl, "CRITICAL", "error: " + "".join(error.args), error_args=error.args)
    logger.stop()
