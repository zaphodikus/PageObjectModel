from selenium.webdriver.common.by import By

# PageObject base classes
from TestBase import PageBaseTest
from PageFactory import WebApplicationStub, PageFactory, PageTitleChecker
from TestBase import POMException

# PageOjects that return fresh Pageobjects
from PageChains import DemoLoginPageUsernameV2, DemoLoginPagePasswordV2

WEB_LOGIN_URL = "http://localhost:8080/loginuser.html"

class DemoLoginPageUsername(PageFactory):

    def __init__(self, driver, url=None):
        super().__init__(driver, url)

    # define locators dictionary where key name will became WebElement using PageFactory
    locators = {
        "editUserName": (By.ID, "usernameOrEmail"),
        "btnContinue": (By.NAME, "Continue")
    }

    def submit(self, username):
        self.editUserName = username               # edtUserName become class variable using PageFactory
        self.btnContinue.click()


class DemoLoginPagePassword(PageFactory):

    def __init__(self, driver):
        super().__init__(driver)

    # define locators dictionary where key name will became WebElement using PageFactory
    locators = {
        "editPassword": (By.ID, "password"),
        "btnLogin": (By.NAME, "LogIn"),
    }

    def submit(self, password):
        self.editPassword = password
        self.btnLogin.click()


class DemoHomePage(PageFactory):
    """
    On home page once logged in,
    we are only interested in the profile page button/icon here
    """
    locators = {
        "btnProfile": (By.NAME, "Profile"),
    }

    def open_profile(self):
        self.btnProfile.click()


class DemoProfilePage(PageFactory):
    # simple page, with only one button we worry about.
    locators = {
        "btnLogout": (By.NAME, "LogOut")
    }

    def logout(self):
        self.btnLogout.click()
        # wait for the promo page scripts to stop
        import time
        time.sleep(2)


class CombineLoginOutSteps(WebApplicationStub):
    """
    Combines (composes) 4 PageObjects
    """
    def login(self, username, password):
        self.get_app().get("http://localhost:8080/loginuser.html")
        pglogin = DemoLoginPageUsername(self.get_app())
        pglogin.submit(username)
        pgsubmit = DemoLoginPagePassword(self.get_app())
        pgsubmit.submit(password)

    def logout(self):
        pgHome = DemoHomePage(self.get_app())
        pgHome.open_profile()
        pgProfile = DemoProfilePage(self.get_app())
        pgProfile.logout()


class TestPageObjects(PageBaseTest):

    def _test_login_smoke(self):
        """
        SMOKE: Ignore this most basic self-test, not terribly neat
        """
        self.get("http://localhost:8080/loginuser.html")
        pglogin = DemoLoginPageUsername(self)
        pglogin.submit("user")
        pgsubmit = DemoLoginPagePassword(self)
        pgsubmit.submit("pass")

    def _test_login_opens_with_url(self):
        """
        SMOKE: Ignore this self-check that the object can take a url to open
        """
        pglogin = DemoLoginPageUsername(self, "http://localhost:8080/loginuser.html")
        pglogin.submit("user")

    def _test_login_logout(self):
        """
        EXAMPLE 1: Of simple page object use
        """
        self.get("http://localhost:8080/loginuser.html")
        pglogin = DemoLoginPageUsername(self)
        pglogin.submit("user")
        pgsubmit = DemoLoginPagePassword(self)
        pgsubmit.submit("pass")

        pgHome = DemoHomePage(self)
        pgHome.open_profile()
        pgProfile = DemoProfilePage(self)
        pgProfile.logout()

    def _test_combine_pages(self):
        """
        EXAMPLE 2: of a composition class to combine Pages
        """
        login = CombineLoginOutSteps(self)
        login.login("user", "pass")

    def _test_combine_pages_mixing(self):
        """
        EXAMPLE 3: Using the composition class and mixing that with direct use of the webdriver.
        And then for fun, use discrete page-objects all off the same webdriver connection
        """
        login = CombineLoginOutSteps(self)
        browser_app = login.get_app()
        login.login("user", "pass")
        login.logout()
        print("=================")
        browser_app.get(WEB_LOGIN_URL)
        pglogin = DemoLoginPageUsername(browser_app)
        pglogin.submit("user")
        pgsubmit = DemoLoginPagePassword(browser_app)
        pgsubmit.submit("pass")

        pgHome = DemoHomePage(browser_app)
        pgHome.open_profile()
        pgProfile = DemoProfilePage(browser_app)
        pgProfile.logout()

    def _test_page_titles(self):
        """
        PageTitleChecker helper class to allow checking the web page title contains a specified substring.
        TitleChecker is most useful to assert that we have navigated to a specific page, but don't care about
        content or errors.
        """
        PageTitleChecker(self, "Goog", "http://www.google.com")

        try:
            PageTitleChecker(self, "Altavista", "http://www.google.com", timeout=2)
            raise Exception("Negative check failure")
        except POMException as ex:
            print(f"Caught a Page-object-model exception:\n   {ex}")
            print("Which is expected, OK")

    def test_page_chaining(self):
        """
        todo:
        """
        login_page = DemoLoginPageUsernameV2({"driver":self,
                                              "url": WEB_LOGIN_URL,
                                              "username": "user",
                                              "password": "pass"}
                                            )
        password_page = login_page.next()
        home_page = password_page.next()
        if home_page != None:
            raise UserWarning("unexpected at this time")
