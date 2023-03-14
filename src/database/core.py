from .base import DbServer, DbSession,DbUser
from typing import List, Optional, Union


class Fdatabase:
    def __init__(self):
        self.session = DbSession
        self.server = DbServer

    def add_server(self, server: DbServer) -> None:
        self.session.add(server)
        self.session.commit()
    
    def get_server(self, server_id: str) -> Optional[DbServer]:
        return self.session.query(self.server).filter_by(id=server_id).first()
    
    def get_servers(self) -> List[DbServer]:
        return self.session.query(self.server).all()
    
    def delete_server(self, server_id: str) -> None:
        server = self.get_server(server_id)
        self.session.delete(server)
        self.session.commit()

    def update_server(self, server_id: str, data: dict) -> None:
        server = self.get_server(server_id)
        if not server:
            return
        for key, value in data.items():
            setattr(server, key, value)
        self.session.commit()


        