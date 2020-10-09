from selenium.webdriver.common.by import By
from PageFactory import PageFactory


class ChainingPageFactory(PageFactory):
    def __init__(self, args):
        # todo: create a superclass to handle this layer
        if 'url' in args.keys():
            super().__init__(args['driver'], args['url'])
        else:
            super().__init__(args['driver'])
        self._args = args
        self._args.pop('url', None)  # subsequent pages don't get give the starting url

    def next(self):
        raise NotImplemented("Must be overriden to return the next PageObject!")


class DemoLoginPageUsernameV2(ChainingPageFactory):

    locators = {
        "editUserName": (By.ID, "usernameOrEmail"),
        "btnContinue": (By.NAME, "Continue")
    }

    def next(self):
        self._submit(self._args['username'])
        return DemoLoginPagePasswordV2(self._args)

    def _submit(self, username):
        self.editUserName = username
        self.btnContinue.click()


class DemoLoginPagePasswordV2(ChainingPageFactory):

    locators = {
        "editPassword": (By.ID, "password"),
        "btnLogin": (By.NAME, "LogIn"),
    }

    def next(self):
        self._submit(self._args['password'])
        return None  # todo: homepage (self._args)

    def _submit(self, password):
        self.editPassword = password
        self.btnLogin.click()
