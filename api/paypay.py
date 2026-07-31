import aiohttp
import uuid
import random
import os
import json

IO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "io")
PAYPAY_DATA_FILE = os.path.join(IO_DIR, "paypay_data.json")

_UA_LIST = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
]

def _ua():
    return random.choice(_UA_LIST)

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
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class PayPayAPI:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.session = None
        self.data = load_json(PAYPAY_DATA_FILE)

    async def login(self, phone: str, password: str, uuid_val: str = None):
        if uuid_val is None:
            uuid_val = str(uuid.uuid4())

        headers = {
            'User-Agent': _ua(),
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://www.paypay.ne.jp',
            'Referer': 'https://www.paypay.ne.jp/app/account/sign-in',
        }
        payload = {
            "scope": "SIGN_IN",
            "client_uuid": uuid_val,
            "grant_type": "password",
            "username": phone,
            "password": password,
            "add_otp_prefix": True,
            "language": "ja"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.paypay.ne.jp/app/v1/oauth/token",
                headers=headers, json=payload, proxy=self.proxy
            ) as r:
                result = await r.json()

        self.data[phone] = {
            "password": password,
            "uuid": uuid_val,
            "result": result
        }
        save_json(PAYPAY_DATA_FILE, self.data)
        return result

    async def login_otp(self, uuid_val: str, otp: str, otp_id: str, otp_pre: str):
        headers = {
            'User-Agent': _ua(),
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://www.paypay.ne.jp',
            'Referer': 'https://www.paypay.ne.jp/app/account/sign-in',
        }
        payload = {
            "scope": "SIGN_IN",
            "client_uuid": uuid_val,
            "grant_type": "otp",
            "otp_prefix": str(otp_pre),
            "otp": otp,
            "otp_reference_id": otp_id,
            "username_type": "MOBILE",
            "language": "ja"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.paypay.ne.jp/app/v1/oauth/token",
                headers=headers, json=payload, proxy=self.proxy
            ) as r:
                res = await r.json()
                try:
                    if res["response_type"] == "ErrorResponse":
                        return "ERR"
                except Exception:
                    return "OK"
        return "ERR"

    async def check_link(self, code: str):
        if "https://" in code:
            code = code.replace("https://pay.paypay.ne.jp/", "")

        headers = {
            "Accept": "application/json, text/plain, */*",
            'User-Agent': _ua(),
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://www.paypay.ne.jp/app/v2/p2p-api/getP2PLinkInfo?verificationCode={code}",
                headers=headers, proxy=self.proxy
            ) as r:
                info = await r.json()

        if info.get("header", {}).get("resultCode") != "S0000":
            return False
        if info.get("payload", {}).get("orderStatus") == "PENDING":
            return info
        return False