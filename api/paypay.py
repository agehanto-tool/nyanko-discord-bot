import aiohttp
import uuid
import random
import os
import json
import datetime

from io.input import PAYPAY_DATA

_UA_LIST = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
　　"Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class PayPayAPI:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.session = None
        self.data = load_json(PAYPAY_DATA)

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
            "phone_number": phone,
            "password": password,
            "device_uuid": uuid_val,
            "client_uuid": uuid_val,
            "access_token": result.get("access_token", ""),
            "refresh_token": result.get("refresh_token", "")
        }
        save_json(PAYPAY_DATA, self.data)
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

    async def receive_link(self, code: str, phone: str, password: str, uuid_val: str, link_password: str = None):
        if "https://" in code:
            code = code.replace("https://pay.paypay.ne.jp/", "")

        base_headers = {
            "Accept": "application/json, text/plain, */*",
            'User-Agent': _ua(),
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"https://www.paypay.ne.jp/app/v2/p2p-api/getP2PLinkInfo?verificationCode={code}",
                    headers=base_headers, proxy=self.proxy
                ) as r:
                    r.raise_for_status()
                    link_info = await r.json()

                if link_info.get("payload", {}).get("orderStatus") != "PENDING":
                    return False
                if link_info.get("payload", {}).get("pendingP2PInfo", {}).get("isSetPasscode") and link_password is None:
                    return False
            except aiohttp.ClientError as e:
                print(f"link_info error: {e}")
                return False

            login_headers = {
                'User-Agent': _ua(),
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'Origin': 'https://www.paypay.ne.jp',
                'Referer': f'https://pay.paypay.ne.jp/{code}',
            }
            login_payload = {
                "scope": "SIGN_IN",
                "client_uuid": uuid_val,
                "grant_type": "password",
                "username": phone,
                "password": password,
                "add_otp_prefix": True,
                "language": "ja"
            }
            async with session.post(
                "https://www.paypay.ne.jp/app/v1/oauth/token",
                headers=login_headers, json=login_payload, proxy=self.proxy
            ) as r:
                login_res = await r.json()
                try:
                    login_res["access_token"]
                except Exception:
                    try:
                        login_res["otp_reference_id"]
                        return "LOGINERR"
                    except Exception:
                        return "LOGINERR"

            receive_payload = {
                "verificationCode": code,
                "client_uuid": uuid_val,
                "requestAt": str(
                    datetime.datetime.now(
                        datetime.timezone(datetime.timedelta(hours=9))
                    ).strftime('%Y-%m-%dT%H:%M:%S+0900')
                ),
                "requestId": link_info["payload"]["message"]["data"]["requestId"],
                "orderId": link_info["payload"]["message"]["data"]["orderId"],
                "senderMessageId": link_info["payload"]["message"]["messageId"],
                "senderChannelUrl": link_info["payload"]["message"]["chatRoomId"],
                "iosMinimumVersion": "3.45.0",
                "androidMinimumVersion": "3.45.0"
            }
            if link_password:
                receive_payload["passcode"] = link_password

            try:
                async with session.post(
                    "https://www.paypay.ne.jp/app/v2/p2p-api/acceptP2PSendMoneyLink",
                    json=receive_payload, headers=base_headers, proxy=self.proxy
                ) as r:
                    r.raise_for_status()
                    res = await r.json()
                    return res.get("header", {}).get("resultCode") == "S0000"
            except aiohttp.ClientError as e:
                print(f"receive error: {e}")
                return False
