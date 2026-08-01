import os
import json

from io.input import KYASH_DATA

try:
    from Kyasher import Kyash
    KYASH_AVAILABLE = True
except:
    KYASH_AVAILABLE = False

def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class KyashAPI:
    def __init__(self):
        self.data = load_json(KYASH_DATA)
        self.instance = None

    def login(self, email: str, password: str, client_uuid: str = None, installation_uuid: str = None):
        if KYASH_AVAILABLE:
            if client_uuid and installation_uuid:
                self.instance = Kyash(email, password, client_uuid, installation_uuid)
            else:
                self.instance = Kyash(email, password)
        self.data[email] = {
            "password": password,
            "client_uuid": client_uuid,
            "installation_uuid": installation_uuid
        }
        save_json(KYASH_DATA, self.data)
        return self.instance

    def login_otp(self, otp: str):
        if self.instance and KYASH_AVAILABLE:
            self.instance.login(otp)
            return True
        return False

    def get_profile(self):
        if self.instance and KYASH_AVAILABLE:
            return self.instance.get_profile()
        return None

    def get_wallet(self):
        if self.instance and KYASH_AVAILABLE:
            return self.instance.get_wallet()
        return None

    def create_link(self, amount: int, message: str = "", is_claim: bool = False):
        if self.instance and KYASH_AVAILABLE:
            return self.instance.create_link(amount=amount, message=message, is_claim=is_claim)
        return None

    def link_check(self, url: str):
        if self.instance and KYASH_AVAILABLE:
            return self.instance.link_check(url)
        return None

    def link_receive(self, url: str = None, link_uuid: str = None):
        if self.instance and KYASH_AVAILABLE:
            return self.instance.link_recieve(url=url, link_uuid=link_uuid)
        return None
