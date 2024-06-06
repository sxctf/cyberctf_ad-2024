import requests, random
from bs4 import BeautifulSoup
from checklib import *

PORT = 10000

Name = ['Vladimir', 'Alexander', 'Stanislav', 'Darina', 'Tatyana', 'Lybov', 'Lora', 'Antonio', 'Mariya', 'Evgeniya', 'Grigory', 'Andrey', 'Pavel', 'Renat', 'Alexey']
City = ['Moscow', 'StPetersburg', 'Novosibirsk', 'Yekaterinburg', 'Nizhny Novgorod', 'Kazan', 'Chelyabinsk','Omsk','Samara',
        'Rostov-on-Don','Ufa','Krasnoyarsk','Voronezh','Perm','Volgograd','Krasnodar','Saratov','Tyumen','Togliatti','Izhevsk',
        'Barnaul','Ulyanovsk','Irkutsk','Khabarovsk','Yaroslavl','Vladivostok','Makhachkala','Orenburg','Tomsk','Kemero']

class CheckMachine:

    def __init__(self, checker):
        self.checker = checker
        

    def ping(self):
        r = requests.get(f'http://{self.checker.host}:{PORT}/', timeout=3)
        self.checker.check_response(r, 'Check failed')

    def put_flag(self, flag_id, flag, vuln):
        rdata = {"name":Name[random.randint(0, len(Name))-1],  
                    "city":City[random.randint(0, len(Name))-1],
                    "place":random.randint(0, 300),
                    "vanNumber": str(random.randint(0, 20))+"/"+str(random.randint(0, 5)),
                    "cardID": flag,
                    "book": "Book+ticket"
                    }
        
        url = f'http://{self.checker.host}:{PORT}/'
        r = requests.post(url, data=rdata, timeout=3)
        self.checker.check_response(r, 'Could not put flag')
        soup = BeautifulSoup(r.text, 'html.parser')
        new_id = soup.find("h1", {"id" : "1"})
        if len(new_id.text) !=  36:
            self.checker.cquit(Status.MUMBLE, 'Services not working correctly', 'Services not working correctly in put_flag')
        return new_id.text

    def get_flag(self, flag_id, vuln):
        
        url = f'http://{self.checker.host}:{PORT}/'
        rdata = {"book_id" : flag_id,
                "check": "Check+ticket"}
        try:
            r = requests.post(url, data=rdata, timeout=3)
            self.checker.check_response(r, 'Could not get flag')
            soup = BeautifulSoup(r.text, 'html.parser')
            flag = soup.find("td", {"id" : "5"})    
            return flag.text
        except IOError as e:
            self.checker.cquit(Status.MUMBLE, 'Services not working correctly', 'Services not working correctly in get_flag')
            
    

        
        
        