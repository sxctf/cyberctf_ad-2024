from pathlib import Path
from checklib import *
import requests

BASE_DIR = Path(__file__).absolute().resolve().parent

PORT = 8000

class CheckMachine:

    def __init__(self, checker):
        self.checker = checker

    def ping(self):
        r = requests.get(f'http://{self.checker.host}:{PORT}/api/healthcheck/?url=http://localhost:5555/api/new_order', timeout=5)
        self.checker.check_response(r, 'Check failed')

        r = requests.get(f'http://{self.checker.host}:{PORT}/api/healthcheck/?url=http://localhost:5555/api/check_order', timeout=5)
        self.checker.check_response(r, 'Check failed')

        r = requests.get(f'http://{self.checker.host}:{PORT}/api/healthcheck/?url=http://localhost:5555/api/order/0', timeout=5)
        self.checker.check_response(r, 'Check failed')

        r = requests.get(f'http://{self.checker.host}:{PORT}/api/healthcheck/?url=http://localhost:5555/api/status/0', timeout=5)
        self.checker.check_response(r, 'Check failed')

        r = requests.get(f'http://{self.checker.host}:{PORT}/api/healthcheck/?url=http://localhost:5555/api/bill/0', timeout=5)
        self.checker.check_response(r, 'Check failed')

        r = requests.get(f'http://{self.checker.host}:{PORT}/api/healthcheck/?url=http://localhost:5555/internal/orders', timeout=5)
        self.checker.check_response(r, 'Check failed')

    def put_flag(self, flag):
        data = {'type': 'Кружка чая', 'username': 'ForcAD', 'coupon': flag}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(f'http://{self.checker.host}:{PORT}/api/new_order', headers=headers, json=data, timeout=5)
        self.checker.check_response(r, 'Could not get flag')
        data = r.json()

        if 'result' in data and data['result'] == "OK" and 'data' in data:
            return data['data']
        else:
            self.checker.check_response(r, 'Could not put flag')
            return ""

    def get_flag(self, flag_id):
        r = requests.get(f'http://{self.checker.host}:{PORT}/api/order/{flag_id}', timeout=5)
        self.checker.check_response(r, 'Could not get flag')
        data = r.json()

        if 'result' in data and data['result'] == "OK" and 'data' in data:
            resData = data['data']
            if 'coupon' in resData and len(resData['coupon']) > 0:
                flag = resData['coupon']
                r = requests.get(f'http://{self.checker.host}:{PORT}/api/bill/{flag_id}', timeout=5)
                self.checker.check_response(r, 'Could not get flag')

                if flag_id in r.text:
                    return flag
                        
        return ""