

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

from selenium.common import exceptions


from typing import List, Optional, Union


class BaseBrowser:
    def __init__(self, headless=False):
        self.headless = headless


        
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('--disable-notifications')

        # disable logging
        self.options.add_argument('--log-level=3')
        self.options.add_argument('--silent')
        self.options.add_argument('--disable-logging')
        self.options.add_argument('--disable-dev-shm-usage')
        # disable images
        self.options.add_argument('--blink-settings=imagesEnabled=false')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        

        if self.headless:
            self.options.add_argument('--headless')

        self.service = Service('config\\chromedriver.exe')
        

        self.driver = webdriver.Chrome(options=self.options, service=self.service)

    def load_cookies(self, cookies : dict):
        # print(cookies)
        for name, value in cookies.items():
            self.driver.add_cookie({'name': name, 'value': value})

        self.driver.refresh()

            

    
    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
        except exceptions.NoSuchElementException:
            return False
        return True
    
    def check_exists_by_id(self, id):
        try:
            self.driver.find_element(By.ID, id)
        except exceptions.NoSuchElementException:
            return False
        return True
    
    def check_exists_by_class(self, class_name):
        try:
            self.driver.find_element(By.CLASS_NAME, class_name)
        except exceptions.NoSuchElementException:
            return False
        return True
    
    
    def wait_for_xpath(self, xpath, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except exceptions.TimeoutException:
            return False
        return True
    
    def wait_for_id(self, id, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.ID, id)))
        except exceptions.TimeoutException:
            return False
        return True
    
    def wait_for_class(self, class_name, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        except exceptions.TimeoutException:
            return False
        return True
    
    
    
        
