from driver import Navegador
import time
import os

cookie = {
    "name": "li_at",
    "value": os.environ["LINKEDIN_COOKIE"],
    "domain": ".linkedin.com"
}

class Linkedin:
    def __init__(self):
        self.driver = Navegador()

    def login(self):
        self.driver.get('https://www.linkedin.com/')
        time.sleep(10)


linkedin = Linkedin()
linkedin.login()
linkedin.driver.driver.add_cookie(cookie)
linkedin.driver.driver.refresh()
time.sleep(10)
