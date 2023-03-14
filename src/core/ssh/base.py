import paramiko

class SSHClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.remote_conn_pre = paramiko.SSHClient()
        self.remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.remote_conn_pre.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)

        # check if connection is established
        if self.remote_conn_pre.get_transport().is_active():
            print("Connection established to {}".format(self.host))
    
    def execute(self, command) -> list:
        stdin, stdout, stderr = self.remote_conn_pre.exec_command(command)
        # read output yield for large output
        for line in stdout.read().splitlines():
            yield line
    
    
    def close(self):
        self.remote_conn_pre.close()
        print("Connection closed to {}".format(self.host))

    def put_file(self, local_path, remote_path, root=False):
        try:
            sftp = self.remote_conn_pre.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print("File {} uploaded to {}".format(local_path, remote_path))
            if root:
                self.execute('chmod +x {}'.format(remote_path))
            return True
        except FileNotFoundError:
            print("File {} not found".format(local_path))
            return None
        
        except Exception as e:
            print("Error: {}".format(e))
            return False


   