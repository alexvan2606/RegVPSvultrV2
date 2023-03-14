import requests
import time
from typing import Dict, Optional

from .errors import VultrAPIError

class VultrAPI:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = 'https://api.vultr.com/v2'
        self.headers: Dict[str, str] = {'Authorization': f'Bearer {api_key}'}

    def request(self, method: str, path: str, data: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        url = f"{self.base_url}/{path}"
        
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response_data = response.json()
            if response.status_code not in range(200, 300):
                raise VultrAPIError(response_data)
            return response_data
        except ValueError:
            raise VultrAPIError(response.text)
        
    
        
        