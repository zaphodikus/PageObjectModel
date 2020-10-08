
from selenium.webdriver.common.by import By
from TestBase import PageBaseTest
from PageFactory import WebApplicationStub, PageFactory, PageTitleChecker
from TestBase import POMException


class CombineLoginOutSteps(WebApplicationStub):
    def login(self, username, password):
        self.get_app().get("http://localhost:8080/loginuser.html")
        pglogin = WPLoginPageUsername(self.get_app())
        pglogin.submit(username)
        pgsubmit = WPLoginPagePassword(self.get_app())
        pgsubmit.submit(password)

    def logout(self):
        pgHome = WPHomePage(self.get_app())
        pgHome.open_profile()
        pgProfile = WPProfilePage(self.get_app())
        pgProfile.logout()


class WPLoginPageUsername(PageFactory):

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


class WPLoginPagePassword(PageFactory):

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


class WPHomePage(PageFactory):
    """
    the workpress home page once logged in,
    we are only interested in the top-right profile page button/icon here
    """
    locators = {
        "btnProfile": (By.NAME, "Profile"),
    }

    def open_profile(self):
        self.btnProfile.click()


class WPProfilePage(PageFactory):
    locators = {
        "btnLogout": (By.NAME, "LogOut")
    }

    def logout(self):
        self.btnLogout.click()
        # wait for the promo page scripts to stop
        import time
        time.sleep(2)

# import unittest
# import time
# class TestWebserver(unittest.TestCase):
#     def test_process(self):
#         svr = WebServer()
#         svr.exec_command(['python', '-m', 'http.server', '80'])
#         time.sleep(1)
#         svr.terminate_command()
#         print("OK")


class TestPageObjects(PageBaseTest):

    def _test_login(self):
        self.get("http://localhost:8080/loginuser.html")
        pglogin = WPLoginPageUsername(self)
        pglogin.submit("user")
        pgsubmit = WPLoginPagePassword(self)
        pgsubmit.submit("pass")

    def _test_login_url(self):
        pglogin = WPLoginPageUsername(self, "http://localhost:8080/loginuser.html")
        pglogin.submit("user")
        pgsubmit = WPLoginPagePassword(self)
        pgsubmit.submit("pass")

    def test_login_logout(self):
        self.get("http://localhost:8080/loginuser.html")
        pglogin = WPLoginPageUsername(self)
        pglogin.submit("user")
        pgsubmit = WPLoginPagePassword(self)
        pgsubmit.submit("pass")

        pgHome = WPHomePage(self)
        pgHome.open_profile()
        pgProfile = WPProfilePage(self)
        pgProfile.logout()

    def test_combine_pages(self):
        login = CombineLoginOutSteps(self)
        login.login("user", "pass")

    def test_combine_pages_many(self):
        login = CombineLoginOutSteps(self)
        browser_app = login.get_app()
        login.login("user", "pass")
        login.logout()
        print("=================")
        browser_app.get("http://localhost:8080/loginuser.html")
        pglogin = WPLoginPageUsername(browser_app)
        pglogin.submit("user")
        pgsubmit = WPLoginPagePassword(browser_app)
        pgsubmit.submit("pass")

        pgHome = WPHomePage(browser_app)
        pgHome.open_profile()
        pgProfile = WPProfilePage(browser_app)
        pgProfile.logout()

    def test_page_titles(self):
        """
        PageTitleChecker helper class to allow checking the web page title contains a specified substring
        :return:
        """
        try:
            page = PageTitleChecker(self, "Altavista", "http://www.google.com", timeout=2)
            raise Exception("Negative check failure")
        except POMException as ex:
            print(f"Caught a Page-object-model exception:\n   {ex}")
            print("Which is expected, OK")
        page = PageTitleChecker(self, "Goog", timeout=2)
