import requests
import random
from bs4 import BeautifulSoup
from checklib import *

PORT = 9000


coolingLevel = ['Extremely Low','Quite Low','Low','Medium','High','Extremely High']
coolingType = ['Air cooling','Liquid cooling','Hybrid', 'Steam cooling', 'Regenerative braking', 'Heat exchanger']


class CheckMachine:

    def __init__(self, checker):
        self.checker = checker

    def ping(self):
        r = requests.get(f'http://{self.checker.host}:{PORT}/', timeout=3)
        r1 = requests.get(f'http://{self.checker.host}:{PORT}/dashboard', timeout=3)
        r2 = requests.get(f'http://{self.checker.host}:{PORT}/coolingSystem/image?filename=col1.png', timeout=3)
        r3 = requests.get(f'http://{self.checker.host}:{PORT}/login', timeout=3)
        r4 = requests.get(f'http://{self.checker.host}:{PORT}/registration', timeout=3)
        r5 = requests.get(f'http://{self.checker.host}:{PORT}/coolingSystem', timeout=3)
        self.checker.check_response(r, 'Check failed')
        self.checker.check_response(r1, 'Check failed')
        self.checker.check_response(r2, 'Check failed')
        self.checker.check_response(r3, 'Check failed')
        self.checker.check_response(r4, 'Check failed')
        self.checker.check_response(r5, 'Check failed')

    def put_flag(self, flag_id, flag, vuln):
        
        rdata = {"coolLevel":coolingLevel[random.randint(0, len(coolingLevel))-1],  
                    "coolFreq":flag,
                    "coolType":coolingType[random.randint(0, len(coolingType))-1],
                    "operation": "Insert"}
        
        url = f'http://{self.checker.host}:{PORT}/coolingSystem'
        r = requests.post(url, data=rdata, timeout=3)
        self.checker.check_response(r, 'Could not put flag')
        soup = BeautifulSoup(r.text, 'html.parser')
        new_id = soup.find("p")
        if len(new_id.text) <  45:
            self.checker.cquit(Status.MUMBLE, 'Services not working correctly', 'Services not working correctly in put_flag')
        return new_id.text[9:45]

    def get_flag(self, flag_id, vuln):
        
        url = f'http://{self.checker.host}:{PORT}/coolingSystem'
        rdata = { "id":flag_id,
                    'operation':"Check" }
        try:
            r = requests.post(url, data=rdata, timeout=3)
            self.checker.check_response(r, 'Could not get flag')
            soup = BeautifulSoup(r.text, 'html.parser')
            flag = soup.find("p")    
            return flag.text[18:-1].split(",")[2].split(":")[1][3:-2]
        except IOError as e:
            self.checker.cquit(Status.MUMBLE, 'Services not working correctly', 'Services not working correctly in get_flag')
            
        
        