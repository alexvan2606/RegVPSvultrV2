from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dataclasses import dataclass

# Kết nối tới database
engine = create_engine('sqlite:///database/servers.db')

# Tạo một class Base dùng để kế thừa cho các class table
Base = declarative_base()

# Tạo class table Server

class DbServer(Base):
    __tablename__ = 'servers'

    id = Column(String, primary_key=True)
    label = Column(String)
    main_ip = Column(String)
    status = Column(String)
    region = Column(String)
    plan = Column(String)
    os = Column(String)
    date_created = Column(String)
    vcpu_count = Column(Integer)
    ram = Column(Integer)
    disk = Column(Integer)
    default_password = Column(String)
    server_status = Column(String)
    setup = Column(Integer)
    def __init__(self, id: str, label: str, main_ip: str, status: str, region: str, plan: str, os: str, date_created: str, vcpu_count: int, ram: int, disk: int, default_password: str, server_status: str = '', setup: int = 0):
        self.id = id
        self.label = label
        self.main_ip = main_ip
        self.status = status
        self.region = region
        self.plan = plan
        self.os = os
        self.date_created = date_created
        self.vcpu_count = vcpu_count
        self.ram = ram
        self.disk = disk
        self.default_password = default_password
        self.server_status = server_status
        self.setup = setup


# # tao một table DbUser có khóa ngoại là id của table DbServer
class DbUser(Base):
    __tablename__ = 'UsersWP'

    id = Column(String, primary_key=True)
    pmadbpass = Column(String)
    pmadbuser = Column(String)
    pmamodalpass = Column(String)
    wpadminpass = Column(String)
    wpadminuser = Column(String)
    xhprofpass = Column(String)
    xhprofuser = Column(String)
    def __init__(self, id: int, pmadbpass: str, pmadbuser: str, pmamodalpass: str, wpadminpass: str, wpadminuser: str, xhprofpass: str, xhprofuser: str):
        self.id = id
        self.pmadbpass = pmadbpass
        self.pmadbuser = pmadbuser
        self.pmamodalpass = pmamodalpass
        self.wpadminpass = wpadminpass
        self.wpadminuser = wpadminuser
        self.xhprofpass = xhprofpass
        self.xhprofuser = xhprofuser





Base.metadata.create_all(engine)

# Tạo một session
DbSession = sessionmaker(bind=engine)()


