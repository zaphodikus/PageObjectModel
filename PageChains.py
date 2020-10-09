from selenium.webdriver.common.by import By
from PageFactory import PageFactory


class ChainingPageFactory(PageFactory):
    def __init__(self, **kwargs):
        # todo: create a superclass to handle this layer
        if 'url' in kwargs.keys():
            super().__init__(kwargs['driver'], kwargs['url'])
        else:
            super().__init__(kwargs['driver'])
        self._kwargs = kwargs
        self._kwargs.pop('url', None)  # subsequent pages don't get give the starting url

    def next(self):
        raise NotImplemented("Must be overriden to return the next PageObject!")


class DemoLoginPageUsernameV2(ChainingPageFactory):

    locators = {
        "editUserName": (By.ID, "usernameOrEmail"),
        "btnContinue": (By.NAME, "Continue")
    }

    def next(self):
        self._submit(self._kwargs['username'])
        return DemoLoginPagePasswordV2(**self._kwargs)

    def _submit(self, username):
        self.editUserName = username
        self.btnContinue.click()


class DemoLoginPagePasswordV2(ChainingPageFactory):

    locators = {
        "editPassword": (By.ID, "password"),
        "btnLogin": (By.NAME, "LogIn"),
    }

    def next(self):
        self._submit(self._kwargs['password'])
        return DemoHomePageV2(**self._kwargs)

    def _submit(self, password):
        self.editPassword = password
        self.btnLogin.click()


class DemoHomePageV2(ChainingPageFactory):
    """
    On home page once logged in,
    we are only interested in the profile page button/icon here
    """
    locators = {
        "btnProfile": (By.NAME, "Profile"),
    }

    def next(self):
        self._open_profile()
        return DemoProfilePageV2(**self._kwargs)

    def _open_profile(self):
        self.btnProfile.click()


class DemoProfilePageV2(ChainingPageFactory):
    # simple page, with only one button we worry about.
    locators = {
        "btnLogout": (By.NAME, "LogOut")
    }

    def next(self):
        self._logout()
        return DemoLoginPageUsernameV2(**self._kwargs)

    def _logout(self):
        self.btnLogout.click()

