

from .base import BaseBrowser

from ..request import RqWordPress

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

from selenium.common import exceptions


class WordPressBrowser(BaseBrowser):
    def __init__(self, data : dict, headless=False):
        super().__init__(headless=headless)
        self.account = data['account']
        self.data = data
        self.host = 'https://' + data['main_ip']
        print(self.host)

    def login(self, log_request : bool = True) -> bool:
        # https://149.248.5.213/wp-admin/
        self.driver.get(self.host + '/wp-login.php')
        if log_request:
            self.base_request = RqWordPress(self.host)
            if self.base_request.login(self.account['username'], self.account['password']):
                cookies = self.base_request.get_cookies()
                self.load_cookies(cookies)
            else:
                return False
                
        elif self.check_exists_by_id('user_login'):
            self.driver.find_element_by_id('user_login').send_keys(self.account['username'])
            self.driver.find_element_by_id('user_pass').send_keys(self.account['password'])
            self.driver.find_element_by_id('wp-submit').click()

        if self.wait_for_id('wp-admin-bar-root-default'):
            return True
        return False
    
    def upload_file(self, file_path : str):
        url = self.host + '/wp-admin/admin.php?page=ai1wm_import'
        self.driver.get(url)
        if self.wait_for_class('ai1wm-button-main'):
            elm = self.driver.find_element(By.CLASS_NAME, 'ai1wm-button-main').click()

            # upload file
            if self.wait_for_id('ai1wm-import-file',timeout=60):
                self.driver.find_element(By.ID, 'ai1wm-select-file').send_keys(file_path)
                if self.wait_for_class('ai1wm-progress-bar',timeout=60):
                    value = self.driver.find_element(By.CLASS_NAME, 'ai1wm-progress-bar-percent').text
                    while value != '100.00%':
                        if self.wait_for_class('ai1wm-progress-bar-percent'):
                            value = self.driver.find_element(By.CLASS_NAME, 'ai1wm-progress-bar-percent')
                            try:
                                value = value.text
                            except exceptions.StaleElementReferenceException:
                                value = '100.00%'
                            #  print(value)
                            # print loading bar
                            print('[' + '#' * int(float(value[:-1]) / 2) + ' ' * (50 - int(float(value[:-1]) / 2)) + ']' + value, end='\r')
                      
                    if self.wait_for_class('ai1wm-button-green',timeout=60):
                        el = self.driver.find_element(By.CLASS_NAME, 'ai1wm-button-green')
                        el.click()
                if self.wait_for_class('ai1wm-title-green',timeout=60):
                    return True
                    


            return True
        return False
  

