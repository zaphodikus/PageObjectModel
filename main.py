# A python unittest app showing browser Page Object Model to simplify app testing.
# Details : https://softcircuitry.blogspot.com/2020/10/selenium-page-objects-1-of-2.html
# This Code : https://github.com/zaphodikus/PageObjectModel
#
from selenium.webdriver.common.by import By
import time

# PageObject base classes
from TestBase import PageBaseTest
from PageFactory import WebApplicationStub, PageFactory, PageTitleChecker
from TestBase import POMException

# PageOjects that return fresh Pageobjects
from PageChains import DemoLoginPageUsernameV2

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

    def _test_page_chaining(self):
        """
        A slightly more refined approach which adds a contract to each page that specifies the page must always
        return a very specific page to you. Depending on your application this approach that uses a decorator
        to cast in stone which Page you end up on will simplify apps so changes in flow can still occur
        under-the-hood.
        """
        print("Chain all the app pages for login logout together one at a time")
        login_page = DemoLoginPageUsernameV2(driver=self,
                                             url=WEB_LOGIN_URL,
                                             username="user",
                                             password="pass"
                                            )
        # after entering a username, we always get to the password page
        password_page = login_page.next()
        # after password we expect to get to the main app page
        home_page = password_page.next()
        # this will always let us open the profile page
        profile_page = home_page.next()
        # a logout will always take us back to the login page
        ending_page = profile_page.next()

        if not isinstance(ending_page, DemoLoginPageUsernameV2):
            raise UserWarning("Expected login page at this time!")

    def test_page_chain_to_profile(self):
        """
        Use a PageObject method that ends up taking us via other pages to the page we want in one go
        """
        print("Repeat, but this time go directly to profile page")
        login_page = DemoLoginPageUsernameV2(driver=self,
                                             url=WEB_LOGIN_URL,
                                             animation_delay=0.5
                                            )
        profile_page = login_page.login_to_profile(username="user",
                                                   password="pass")
        # a logout will always take us back to the login page
        ending_page = profile_page.next()

        if not isinstance(ending_page, DemoLoginPageUsernameV2):
            raise UserWarning("Expected login page at this time!")
