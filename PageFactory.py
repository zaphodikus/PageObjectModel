import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *

# PageObject base classes
from TestBase import Logger, DEFAULT_TIMEOUT, POMException

ANIMATION_DELAY = 1  # make this 0 when you want to run fast as possible

class PageFactory(Logger):
    # To use this page object declare locators in your child class
    #locators = {
    # "editUserName": (By.ID, "usernameOrEmail"),
    # "btnContinue": (By.XPATH, "//button[contains(.,\'Continue\')]")
    # }
    # When instantiated, the Page will check that the elements are present and return you an object that defines
    # properties that will return the element, or call send_keys() upon assignment. Example:
    # self.editUserName = "JoeBloggs"
    # if self.editUserName.text != "JoeBloggs":
    #   print("Oops, that should not happen!")

    def __init__(self,
                 base,
                 url=None,
                 wait_title_contains=None,
                 timeout=DEFAULT_TIMEOUT,
                 highlight=True,
                 animation_delay=ANIMATION_DELAY):
        """

        :param base: a PageBaseTest object
        :param url: optional url to navigate to first
        :param wait_title_contains: optional case-sensitive page title substring to wait for
        :param timeout: seconds
        :param highlight: highlight elements as we use them
        :param animation_delay: wait after most actions (a demo/debugging aid)
        """
        super().__init__("POM")  # logger prefix
        # It is necessary to initialise driver as page class member to implement Page Factory
        self.driver = base.get_webdriver()
        self.timeout = DEFAULT_TIMEOUT
        self.set_timeout(timeout)
        self._highlight = highlight
        self._delay = 0  # disable getter delays during object init

        if url:
            self._pre_navigate(url)
        if wait_title_contains:
            self.log(f"Wait for title to contain '{wait_title_contains}'")
            if not self._is_title_containing(wait_title_contains):
                raise POMException(self.driver, f"Expected page title containing '{wait_title_contains}' not found.")
        if not self._are_locators_loaded():
            raise POMException(self.driver, "One or more locators on this page were not found.")
        self._delay = animation_delay

    def set_timeout(self, to):
        self.timeout = to

    def _pre_navigate(self, url):
        self.log(f"pre_navigate:{url}")
        self.driver.get(url)

    def _is_title_containing(self, expect_title_contains):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.title_contains(expect_title_contains)
            )
            return True
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as ex:
            self.log(f"Page {self.driver.current_url} title = '{self.driver.title}'")
        return False

    def _are_locators_loaded(self):
        """
        True if the page fails to present the desired locators
        :return: True or False
        """
        loaded = True
        for key in self.locators:  # these must be defined in the derived class
            try:
                WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_element_located((self.locators[key][0], self.locators[key][1]))
                )
            except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as ex:
                self.log(f"Page {self.driver.current_url} did not contain {self.locators[key][0]}" +
                         f"{self.locators[key][1]}")
                loaded = False
        return loaded

    def _ensure_visible(self,
                        by: webdriver.common.by,
                        criteria: str):
        """
        Wait for element to exist, and scroll it into view, but NOT checking that it is enabled
        """
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located((by, criteria))
        )
        # scroll to visible
        action = ActionChains(self.driver)
        action.move_to_element(element).perform()
        return element

    # todo: add a getattr and setattr to magically drive locators as object properties
    def __getattr__(self, alias):
        """
        Attribute lookup helper, will return a webelement that is scrolled into view and visible, else will raise
        :param alias: the key in the lookup dictionary
        :return: webelement
        """
        if alias == "locators":
            raise Exception("A PageFactory class locators dict was not defined!")
        if alias != "__len__":
            self.log(f"__getattr__ {alias}")

        if alias in self.locators.keys():
            locator = self.locators[alias]
            # wait for element to be present
            element = self._ensure_visible(locator[0], locator[1])
            if self._highlight: self.highlight_web_element(element)
            if self._delay: time.sleep(self._delay)
            return element
        else:
            raise Exception(
                f"No page element with the alias {alias} was defined!\nTry adding it to the locators dictionary."
            )

    def __setattr__(self, alias, value):
        if alias in self.locators.keys():
            self.log(f"__setattr__ {alias} = '{value}'")
            locator = self.locators[alias]
            # wait for element to be present
            element = self._ensure_visible(locator[0], locator[1])
            if self._highlight: self.highlight_web_element(element)
            element.clear()
            element.send_keys(value)
        else:
            super(PageFactory, self).__setattr__(alias, value)

    def highlight_web_element(self, element):
        """
        To highlight webElement with magenta border
        :param: WebElement
        :return: None
        """
        if self._highlight:
            self.driver.execute_script("arguments[0].style.border='3px ridge #ff33ff'", element)

class PageTitleChecker(PageFactory):

    def __init__(self, base, wait_title_contains, url=None, timeout=DEFAULT_TIMEOUT):
        """
        A test page object that has no locators on the page, and only waits for the page title to change
        :param base: a PageBaseTest object
        :param wait_title_contains: optional case sensitive page title substring to wait for
        :param timeout: seconds
        """
        super().__init__(base, url, wait_title_contains, timeout)  # logger prefix

    locators = {}


class WebApplicationStub(object):
    """
    A stub class that lets us combine more naturally combine multiple PageObjects into workflows with multiple pages
    """
    def __init__(self, app):
        """
        :param app: the test or PageBaseTest instance
        """
        self._webapp = app

    def get_app(self):
        """
        Gives the instance of the "TestBase" for this testcase
        :return: a PageBaseTest
        """
        return self._webapp

