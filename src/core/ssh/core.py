from .base import SSHClient


class Fssh:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = SSHClient(self.host, self.port, self.username, self.password)



    def check_path_exist(self, path):
        
        self.client.remote_conn_pre.exec_command('ls {}'.format(path))

    def install(self):
        try:
            # put file to server
            sftp = self.client.put_file('database\\install.sh', '/root/app_binaries/install.sh', root=True)
            if sftp is None:
                return True
            
            # execute file
            stdout = self.client.execute('bash /root/app_binaries/install.sh')
            # read output

            for line in stdout:
                print(line)
            return True
        except Exception as e:
            print(e)
            return False
    
    def getvar(self):
        try:
            sftp = self.client.put_file('database\\getvar.sh', '/root/getvar.sh', root=True)
            df = [
                "pmadbpass",
                "pmadbuser",
                "pmamodalpass",
                "wpadminpass",
                "wpadminuser",
                "xhprofpass",
                "xhprofuser"
            ]
            stdout = self.client.execute('bash /root/getvar.sh')
            dfc = {}
            for line in stdout:
                dfc[df.pop(0)] = line.decode('utf-8')
            return dfc
        except Exception as e:
            print(e)
            return False

    