# This collection of page objects use a decorator to explicitly chain a page directly to another
# using a decorator. By doing a little extra work the idea that a page will always take you to a
# the same eventual page is mandated in code. The decorator below constructs the target page,
# unless the current page throws an exception, which creates more certainty when writing code.
#
# If a page has to deal with intervening page branches or runtime variation, it becomes incumbent
# on the implementor to implement the branches and still return just one page.

from selenium.webdriver.common.by import By
from PageFactory import PageFactory

MAP = {}  # Page objects can add themselves to this map to use the @next_page decorator
# This allows us to reference classes before their definitions are known
def register_page(page_class):
    MAP[page_class.__name__] = page_class


# You can decorate the page next() method if the page is added to the MAP
def next_page(next_):
    def deco(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            return MAP[next_](**self._kwargs)
        return wrapper
    return deco


class ChainingPageFactory(PageFactory):
    def __init__(self, **kwargs):
        # the starting page in a chain of pages may have a URL
        if 'url' in kwargs.keys():
            super().__init__(kwargs['driver'], kwargs['url'])
        else:
            super().__init__(kwargs['driver'])
        # remove url, subsequent pages don't use the starting url
        self._kwargs = kwargs
        self._kwargs.pop('url', None)

    def next(self):
        raise NotImplemented("Must be implemented to return the Chained PageObject!")


class DemoLoginPageUsernameV2(ChainingPageFactory):

    locators = {
        "editUserName": (By.ID, "usernameOrEmail"),
        "btnContinue": (By.NAME, "Continue")
    }

    @next_page("DemoLoginPagePasswordV2")
    def next(self, username):
        self._submit(username)
        return self

    def _submit(self, username):
        self.editUserName = username
        self.btnContinue.click()

    @next_page("DemoProfilePageV2")
    def login_to_profile(self, username, password):
        """
        Does the whole shebang in one go - show how to make sure we always return the object the decorator
        says we should do.
        All the other parameters get passed at construction time via self._kwargs:
        :param password: password
        :return: the profile page
        """
        password_page = self.next(username)
        # after password we expect to get to the main app page
        home_page = password_page.next(password)
        # this will always let us get the Profile page Object
        return home_page.next()


register_page(DemoLoginPageUsernameV2)


class DemoLoginPagePasswordV2(ChainingPageFactory):

    locators = {
        "editPassword": (By.ID, "password"),
        "btnLogin": (By.NAME, "LogIn"),
    }

    @next_page("DemoHomePageV2")
    def next(self, password):
        self._submit(password)
        return self

    def _submit(self, password):
        self.editPassword = password
        self.btnLogin.click()


register_page(DemoLoginPagePasswordV2)


class DemoHomePageV2(ChainingPageFactory):
    """
    On home page once logged in,
    we are only interested in the profile page button/icon here
    """
    locators = {
        "btnProfile": (By.NAME, "Profile"),
    }

    @next_page("DemoProfilePageV2")
    def next(self):
        self._open_profile()
        return self

    def _open_profile(self):
        self.btnProfile.click()


register_page(DemoHomePageV2)


class DemoProfilePageV2(ChainingPageFactory):
    # simple page, with only one button we worry about.
    locators = {
        "btnLogout": (By.NAME, "LogOut")
    }

    @next_page("DemoLoginPageUsernameV2")
    def next(self):
        self._logout()
        return self

    def _logout(self):
        self.btnLogout.click()


register_page(DemoProfilePageV2)
