# unit testing fixtures, replace these with your test framework's own classes and fixtures
import sys
import unittest
import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
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

class WrapDriver(object):
    @staticmethod
    def get_manager():
        raise NotImplemented

    @staticmethod
    def get_driver(bin_path):
        raise NotImplemented


class WrapChrome(WrapDriver):
    @staticmethod
    def get_manager():
        #return ChromeDriverManager()
        return GeckoDriverManager()

    @staticmethod
    def get_driver(bin_path):
        #return webdriver.Chrome(bin_path)
        return webdriver.Firefox(bin_path)


class WrapFireFox(WrapDriver):
    @staticmethod
    def get_manager():
        return GeckoDriverManager()

    @staticmethod
    def get_driver(bin_path):
        ff_options = webdriver.FirefoxOptions()
        #'size': {'width': 1000, 'height': 1000},
        #'position': {'x': 0, 'y': 0}
        ff_options.add_argument("--width=800")
        ff_options.add_argument("--height=1100")
        capabilities = ff_options.to_capabilities()

        wd = webdriver.Firefox(executable_path=bin_path, capabilities=capabilities)
        wd.set_window_position(-5, 0)  # on Windows, Firefox seems to add the system metric SM_CXBORDER
        return wd



class WebAppBase(object):
    """
    Base class for a test case 'session' or 'App' , this is a wrapper for any
    webdriver messiness
    """
    _path = None
    webdriver = None
    browser = "chrome"  # see set_browser
    _browsers = {"chrome": WrapChrome,
                 "firefox" : WrapFireFox}
    log = Logger("BAS")

    @classmethod
    def set_browser(cls, browser_name):
        if browser_name not in cls._browsers.keys():
            raise NotImplemented
        cls.browser = browser_name

    @classmethod
    def start_browser(cls):

        WebAppBase.webdriver = cls._browsers[cls.browser].get_driver(cls._get_drv_path())

    @classmethod
    def _get_drv_path(cls):
        if not WebAppBase._path:
            #WebAppBase._path = ChromeDriverManager().install()
            cls.log.log(f"Find path to {cls.browser} driver...")
            manager = cls._browsers[cls.browser].get_manager()
            WebAppBase._path = manager.install()
            cls.log.log(f"Bin = {WebAppBase._path}")
        return WebAppBase._path

    def get_webdriver(self):
        return WebAppBase.webdriver

    def get(self, url):
        WebAppBase.webdriver.get(url)


class PageBaseTest(unittest.TestCase, WebAppBase):
    log = Logger("PB")
    dummy_web_server = None

    def setUp(self):
        WebAppBase.set_browser("firefox")  # firefox or chrome
        PageBaseTest.log.log(f"setUp: open {WebAppBase.browser}")
        WebAppBase.start_browser()

    def tearDown(self):
        PageBaseTest.log.log("tearDown: quit web driver")
        PageBaseTest.webdriver.quit()

    def get(self, url):
        PageBaseTest.log.log(f"navigate: {url}")
        super().get(url)

    @classmethod
    def setUpClass(cls):
        # start a web server
        PageBaseTest.dummy_web_server = WebServer()
        executable = sys.executable
        PageBaseTest.dummy_web_server.exec_command([executable, '-m', 'http.server', '8080'])

    @classmethod
    def tearDownClass(cls):
        # stop it
        if PageBaseTest.dummy_web_server:
            PageBaseTest.dummy_web_server.terminate_command()


