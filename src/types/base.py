

from typing import Optional, List

from dataclasses import dataclass




@dataclass
class IServer:
    id : str
    os : str
    ram : int
    disk : int
    main_ip : str
    vcpu_count : int
    region : str
    plan : str
    date_created : str
    status : str

