
import time,base64


from typing import Dict,Union,Optional,List


from ..api import VultrAPI






# interface Server {


class VultrServer:
    def __init__(self, api_key: str) -> None:

        self.api = VultrAPI(api_key)

    # def create_ssh_keys(self, name: str, ssh_key: str) -> Dict[str, str]:

    #     data = {'name': name, 'ssh_key': ssh_key}
    
    #     response_data = self.api.request('post', 'ssh-keys', data)
    
    #     return response_data['ssh_key']['id']

    def get_servers(self) -> Dict[str, str]:

        response_data = self.api.request('get', 'instances')

        return response_data['instances']

    def create_server(self, data: Dict[str, str], ssh_keys: Union[str, List[str]] = None) -> Dict[str, str]:
        if ssh_keys:
            if isinstance(ssh_keys, str):
                ssh_keys = [ssh_keys]
            data['sshkey_id'] = ssh_keys

       



        response_data = self.api.request('post', 'instances', data)
   
   
    
        return response_data['instance']
    
    def start_server(self, server_id: str) -> str:
        response_data = self.api.request('post', f'instances/{server_id}/start')
        return response_data['status']
    
    def stop_server(self, server_id: str) -> str:
        response_data = self.api.request('post', f'instances/{server_id}/halt')
        return response_data['status']
    
    def delete_server(self, server_id: str) -> str:
        response_data = self.api.request('delete', f'instances/{server_id}')
        return response_data['status']
    
    def get_user_data(self, server_id: str) -> str:
        response_data = self.api.request('get', f'instances/{server_id}/user-data')
        user_data = response_data['user_data']
        print(user_data)
        return base64.b64decode(user_data).decode('utf-8')
    
    def get_info(self, server_id: str) -> Dict[str, str]:
        response_data = self.api.request('get', f'instances/{server_id}')
        return response_data['instance']
    
    def get_plans(self, meta = False) -> Dict[str, str]:
        
        response_data = self.api.request('get', 'plans-metal' if meta else 'plans')
        return response_data['plans_metal'] if meta else response_data['plans']
        

    # def check_server_status(self) -> str:
    #     while True:
    #         response_data = self.get_info()
    #         if response_data['status'] == 'active':
    #             return response_data['status']
    #         time.sleep(5)
    #     return status