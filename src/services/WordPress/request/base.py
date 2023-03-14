

import requests, json,re

from bs4 import BeautifulSoup
from typing import Dict, Optional
class RqWordPress:
    def __init__(self, host : str) -> None:
        self.session = requests.Session()
        self.host = host
        self.is_login = False





  


    def login(self, username : str, password : str) -> bool:
        login_url = self.host + '/wp-login.php'
        response = self.session.get(login_url,verify=False)
        hidden_fields = {
            field['name']: field['value']
            for field in BeautifulSoup(response.text, 'html.parser').find_all('input', {'type': ['hidden', 'submit']})
        }

        hidden_fields['log'] = username
        hidden_fields['pwd'] = password

        response = self.session.post(login_url, data=hidden_fields,verify=False)
        if response.status_code == 200 and 'wp-admin' in response.url:
            self.is_login = True
            return True
        return False
    
    def get_cookies(self) -> Dict[str, str]:
        return self.session.cookies.get_dict()


