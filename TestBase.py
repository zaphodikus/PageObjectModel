# unit testing fixtures, replace these with your test framework's own classes and fixtures

import unittest
import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from WebServer import WebServer


DEFAULT_TIMEOUT = 20


class Logger(object):
    def __init__(self, name):
        self.name = name

    def log(self, message):
        time = datetime.datetime.utcnow().strftime("%H:%M:%S")
        print(f"[{time}][{self.name}] {message}")


class POMException(Exception):
    def __init__(self, driver, msg):
        self.url = driver.current_url
        self.msg = msg
        # take a screenshot and link it
        file = self.get_temp_filename()
        driver.get_screenshot_as_file(file)
        self.screenshot = file

    def get_temp_filename(self):
        import tempfile
        import os
        return os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()) + '.png')


class WebAppBase(object):
    """
    Base class for a test case 'session' or 'App' , this is a wrapper for any webdriver messiness
    """
    _path = None
    webdriver = None

    @classmethod
    def start_browser(cls):
        WebAppBase.webdriver = webdriver.Chrome(cls._get_drv_path())

    @classmethod
    def _get_drv_path(cls):
        if not WebAppBase._path:
            WebAppBase._path = ChromeDriverManager().install()
        return WebAppBase._path

    def get_webdriver(self):
        return WebAppBase.webdriver

    def get(self, url):
        WebAppBase.webdriver.get(url)


class PageBaseTest(unittest.TestCase, WebAppBase):
    log = Logger("PB")
    dummy_web_server = None

    def setUp(self):
        PageBaseTest.log.log("setUp: open chromedriver")
        WebAppBase.start_browser()

    def tearDown(self):
        PageBaseTest.log.log("teardown: quit chromedriver")
        PageBaseTest.webdriver.quit()

    def get(self, url):
        PageBaseTest.log.log(f"navigate: {url}")
        super().get(url)

    @classmethod
    def setUpClass(cls):
        # start a web server
        PageBaseTest.dummy_web_server = WebServer()
        PageBaseTest.dummy_web_server.exec_command(['python', '-m', 'http.server', '8080'])

    @classmethod
    def tearDownClass(cls):
        # stop it
        if PageBaseTest.dummy_web_server:
            PageBaseTest.dummy_web_server.terminate_command()


