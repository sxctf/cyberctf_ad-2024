import requests
from checklib import *
import re


PORT = 11000
usernameArray = ['elPiniato','UnicornImagination', 'LongBeardedSheep', 'RomanticGiraffe', 'MrBalalaika', 'LadyFirework', 'GiantDandelion', 'SuperBaby', 'PenguinNutella', 'BatSlipper', 'CatFrankfurter', 'MoonRabbit', 'VirusCompilux', 'BraveRubiksCube', 'PrincessBooger', 'ZombieTomato', 'SantaSteel', 'DoctorPineappleJam']
passwordArray = ['asd34dsa6','3ShGR9JmZ2',          'P7THgcm4bW',     'p6HwW8E7qa',       'hHBFYnrbV8',     'Tc3SZjCn2N', 'ebt2xaFqR8',  'Hx3XrpydsD',   'TFBZnqyNSa',   'pEsktzFKGM',   'WuAsZ29PHF',   'nzgeQJ6vtj',   'bK4FNWJ8CY',   'aCfm2HXUQG',   'hB56MUAVrd',       'tKJ7jGkEDd',       'YKHw3vUfTC','KVRmFPhf7B']

class CheckMachine:


    def __init__(self, checker):
        self.checker = checker

    def ping(self):
        r = requests.get(f'http://{self.checker.host}:{PORT}/', timeout=3)
        r1 = requests.get(f'http://{self.checker.host}:{PORT}/logout', timeout=3)
        r2 = requests.get(f'http://{self.checker.host}:{PORT}/registration', timeout=3)
        r3 = requests.get(f'http://{self.checker.host}:{PORT}/login', timeout=3)
        r4 = requests.get(f'http://{self.checker.host}:{PORT}/status', timeout=3)
        r5 = requests.get(f'http://{self.checker.host}:{PORT}/accounting', timeout=3)
        r6 = requests.get(f'http://{self.checker.host}:{PORT}/cargo', timeout=3)
        r7 = requests.get(f'http://{self.checker.host}:{PORT}/station', timeout=3)

        #Get-запрос на /чек выдает 500, если флаг не найден в локальной таблице
        #r8 = requests.get(f'http://{self.checker.host}:{PORT}/checker', timeout=3)
        
        self.checker.check_response(r, 'Check failed')
        self.checker.check_response(r1, 'Check failed')
        self.checker.check_response(r2, 'Check failed')
        self.checker.check_response(r3, 'Check failed')
        self.checker.check_response(r4, 'Check failed')
        self.checker.check_response(r5, 'Check failed')
        self.checker.check_response(r6, 'Check failed')
        self.checker.check_response(r7, 'Check failed')
        #self.checker.check_response(r8, 'Check failed')

    def put_flag(self, flag_id, flag,vuln):
        host_id = str(self.checker.host)
        octets = host_id.split('.')
        host_id = octets[2]
        host_id = int(host_id)
        if int(host_id) > 17:
            host_id = 4

        rdata = {"id":flag_id, "value":flag}
        registerurl = f'http://{self.checker.host}:{PORT}/registration'
        loginurl = f'http://{self.checker.host}:{PORT}/login'
        cargogurl = f'http://{self.checker.host}:{PORT}/cargo'
        stationurl = f'http://{self.checker.host}:{PORT}/station'
        try:
            r = requests.post(registerurl, data= {'username': usernameArray[host_id], 'password' : passwordArray[host_id]}, timeout=50)
            self.checker.check_response(r, 'Could not put flag')
            if "<li>Учетная запись занята</li>" in r.text:
                r = requests.post(loginurl, data = {'username': usernameArray[host_id], 'password' : passwordArray[host_id]}, timeout = 50)
                jwt = r.cookies.get("jwt")
                cookies = {'jwt': jwt}
                r = requests.get(stationurl, timeout=3)
                r = requests.post(stationurl, cookies=cookies, data = {'AddCargoButton':'AddCargoButton', 'AddedCargoTypeArrayDropdown':'Наука', 'AddedCargoName':flag_id, 'AddedCargoAmount': '1', 'AddedCommentCargoSteal': flag})
            if "<li>Успешная регистрация</li>" in r.text:
                r = requests.post(loginurl, data = {'username': 'Alex', 'password' : '53967b964ff4e8844b1'}, timeout = 50)
                jwt = r.cookies.get("jwt")
                cookies = {'jwt': jwt}
                r = requests.get(stationurl, timeout=3)
                r = requests.post(stationurl, cookies=cookies, data = {'AddCargoButton':'AddCargoButton', 'AddedCargoTypeArrayDropdown':'Наука', 'AddedCargoName':flag_id, 'AddedCargoAmount': '1', 'AddedCommentCargoSteal': flag})
            return flag_id
        except Exception as e:
            print(str(e))
            self.checker.cquit(Status.MUMBLE, 'Services not working correctly', 'Services not working correctly in put_flag')

    def get_flag(self, flag_id,vuln):
        registerurl = f'http://{self.checker.host}:{PORT}/registration'
        loginurl = f'http://{self.checker.host}:{PORT}/login'
        cargogurl = f'http://{self.checker.host}:{PORT}/cargo'
        stationurl = f'http://{self.checker.host}:{PORT}/station'
        try:
            host_id = str(self.checker.host)
            octets = host_id.split('.')
            host_id = octets[2]
            host_id = int(host_id)
            if int(host_id) > 17:
                 host_id = 4
            r = requests.post(loginurl, data = {'username': usernameArray[host_id], 'password' : passwordArray[host_id]}, timeout = 50)
            jwt = r.cookies.get("jwt")
            cookies = {'jwt': jwt}
            r = requests.get(cargogurl, timeout=3)
            match = re.search(r"\<pre\>(.*?3)\: (\d+)",r.text)
            passw = match.group(2)
            r = requests.post(stationurl, cookies=cookies, data = {'passScienceSteal':passw, 'ScienceSteal':'ScienceSteal','cargoScienceName':flag_id})
            match = re.search(r"<li>(?!<a>)(.*?)<\/li>",r.text)
            return match.group(1)
            #return flag.text[18:-1].split(",")[2].split(":")[1][3:-2]
        except Exception as e:
            self.checker.cquit(Status.MUMBLE, 'Services not working correctly', 'Services not working correctly in get_flag')
            print(e)