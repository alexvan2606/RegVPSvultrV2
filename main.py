

from dotenv import load_dotenv
import os,json,time,threading
from datetime import datetime

load_dotenv()


from src.core import VultrServer
from src.types.base import IServer
from src.database import Fdatabase,DbServer,DbUser,DbSession
from src.core.ssh import Fssh
from src.services.WordPress import WordPressBrowser

from typing import List



class Main:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.db = Fdatabase()
        self.vultr_server = VultrServer(self.api_key)
    def  create_server(self, timeout: int = 60, check_boot: bool = False) -> IServer:
        # Thực hiện các lệnh bạn muốn tại đây
        label = 'host-' + datetime.now().strftime('%Y-%m-%d')
        data = {
            'region': 'lax',
            'plan': 'vhp-1c-2gb-intel',
            'hostname': label,
            'label': label,
            'image_id':'wordpress'
        }
        server = self.vultr_server.create_server(data)


        dc = DbServer(
            id=server['id'],
            os=server['os'],
            ram=server['ram'],
            label=server['label'],
            disk=server['disk'],
            main_ip=server['main_ip'],
            vcpu_count=server['vcpu_count'],
            region=server['region'],
            plan=server['plan'],
            date_created=server['date_created'],
            status=server['status'],
            default_password = server['default_password']
        )
        self.db.add_server(dc)
        return self.wait_server(server,timeout,check_boot)

    def wait_server(self, server: IServer, timeout: int = 60, check_boot: bool = False):
        while True:
            info = self.vultr_server.get_info(server_id=server['id'])
            if info['status'] == 'active':
                self.db.update_server(server['id'],{
                    'status': info['status'],
                    'main_ip': info['main_ip'],
                    'server_status':info['server_status']
                })
                if check_boot:
                    if info['server_status'] == 'ok':
                        return info
                    else:
                        time.sleep(timeout)
                        continue
                return info
                
            elif check_boot:
                time.sleep(timeout)

    def upload_file_inplugin(self, server : DbServer):
        db_user = self.db.session.query(DbUser).filter_by(id=server.id).first()
        try:
            bd = WordPressBrowser({
                'main_ip': server.main_ip,
                'account': {
                    'username': 'wpauser'+db_user.wpadminuser,
                    'password': db_user.wpadminpass
                }
            },headless=True) 
            if bd.login(log_request=True):
                path = os.path.join(os.getcwd(),'config','test.wpress')
                if bd.upload_file(path):
                    self.db.update_server(server.id,{
                        'setup': 2
                    })
            else:
                self.db.update_server(server.id,{
                    'setup': 2
                })
        except Exception as e:
            print(f"Server {server.id} lỗi {e}")

    

    def get_var(self, server : DbServer):
        ssh = Fssh(
            server.main_ip,port=22,username='root',password=server.default_password
        )
        print('Server {} đang được lấy thông tin'.format(server.id))
        df = ssh.getvar()

        if isinstance(df,dict):
            dk = DbUser(id=server.id,pmadbpass=df['pmadbpass'],pmadbuser=df['pmadbuser'],pmamodalpass=df['pmamodalpass'],wpadminpass=df['wpadminpass'],wpadminuser=df['wpadminuser'],xhprofpass=df['xhprofpass'],xhprofuser=df['xhprofuser'])
            self.db.session.add(dk)
            self.db.session.commit()
            print('Server {} đã được lưu thông tin'.format(server.id))
        else:
            print('Server {} lỗi'.format(server.id))
            


        

                
    def install_server(self, server : DbServer):
        ssh = Fssh(
            server.main_ip,port=22,username='root',password=server.default_password
        )
        if ssh.install():
            self.db.update_server(server.id,{
                'setup': 1
            })
            print('Server {} đã được cài đặt'.format(server.id))
        else:
            print('Server {} lỗi'.format(server.id))
        ssh.client.remote_conn_pre.close()

    def run(self):
        while True:
            os.system('cls')
            ot = input('1 : Create server\n2 : Install server\n3 : Upload file\n4 : Check server\n5 : Exit\nVui lòng chọn : ')
            if ot == '1':
                soluong = int(input('Số lượng server muốn tạo : '))
                for i in range(soluong):
                    server = self.create_server()
                    print('Server {} đã được tạo'.format(server['id']))
                input('Nhấn enter để tiếp tục')
            elif ot in ['2','3']:
                servers = self.db.get_servers()
                for server in servers:
                    
                    if server.server_status == 'ok':
                        if ot == '2':
                            if server.setup == 0:
                                print('Server {} đang được cài đặt'.format(server.id))
                                self.get_var(server)
                                self.install_server(server)
                                
                            else:
                                print('Server {} đã được cài đặt'.format(server.id))
                        elif ot == '3':
                            
                            if server.setup == 1:
                                print('Server {} đang được upload file'.format(server.id))
                                self.upload_file_inplugin(server)




                            elif server.setup == 0:
                                print('Server {} chưa được cài đặt'.format(server.id))
                            else:
                                print('Server {} đã được upload rồi'.format(server.id))
                    else:
                        print('Server {} chưa được boot'.format(server.id))

                        
            elif ot == '4':
                servers = self.db.get_servers()
                for i in servers:
                    info = self.vultr_server.get_info(server_id=i.id)

        
                    print('Server {} đang được check'.format(info['id']))
                    self.db.update_server(info['id'],{
                        'status': info['status'],
                        'server_status':info['server_status']
                    })
                    print('Server {} IP : {} Status : {} Server status : {}'.format(i.id,i.main_ip,info['status'],info['server_status']))
            elif ot == '5':
                exit()
                   


            input('\nNhấn enter để tiếp tục')




    


                
                

   
  

if __name__ == '__main__':
    main = Main(api_key=os.getenv('VULTR_API_KEY'))
    main.run()
