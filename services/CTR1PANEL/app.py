from flask import Flask, redirect, render_template, request, url_for, flash, session, make_response
from flask_login import LoginManager,login_user,login_required, logout_user
import models
import array
import xml.etree.ElementTree as ET
import uuid
from datetime import datetime
from random import randint
import re
import jwt
import psycopg2
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = '66b1132a0173910b01ee3a15ef4e69583bbf2f7f1e4462c99efbe1b9ab5bf808'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
userlogin = ""
    # тип - успех, отказ
    # Дата, время, тип события, имя пользователя, результат
    # >1 МБ - создаем новый файл  .log.1

logging.basicConfig(filename="logs/app.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger('my_logger')
logger.addHandler(RotatingFileHandler(
       filename="logs/app.log", 
       mode='a', 
       maxBytes=1024*1024, 
       backupCount=100))

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    response = make_response(render_template("login.html",cookies = request.cookies))
    response.set_cookie("jwt","")
    flash("Вы вышли из аккаунта","success")
    return response

@app.route('/registration', methods=['GET','POST'])
def registration():
    if request.method == "GET":
        return render_template("registration.html")
    
    if request.method == "POST":
        login = str(request.form['username'])
        password = str(request.form['password'])
        if not validate(str(login)):
            flash("Допускается вводить только буквы и цифры")
            logger.warning("%s Ошибка валидации логина при входе: %s" %(request.remote_addr,str(login)))
            return render_template("registration.html")
        if not validate(str(password)):
            flash("Допускается вводить только буквы и цифры")
            logger.warning("%s Ошибка валидации пароля при входе: %s" %(request.remote_addr,str(password)))
            return render_template("registration.html")

        out = models.getUser(login)
        if len(out)== 0:
            models.insertUser(login,password)
            logger.info("%s Успешная регистрация: %s:%s" %(request.remote_addr,login,password))
            flash("Успешная регистрация")
            return redirect(url_for('login'))
        else:
            flash("Учетная запись занята")
            logger.warning("%s Учетная запись %s занята" %(request.remote_addr,login))

            return render_template('registration.html')
        return render_template("status.html",workersAmount = models.getWorkersAmount('\'Head\''), 
            headVagonStatus = models.getVagonStatus('\'Head\''), 
            capitansList = models.getCapitansList(), 
            timeToStation = getTime(),
            accountingStatus = models.getAccountingStatus("Accounting"), 
            accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
            cargoAmount= models.getAllCargoAmount(), cargoVagonStatus = models.getVagonStatus('\'Cargo\'') )

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = str(request.form['username'])
        password = str(request.form['password'])
        if not validate(str(username)):
            flash("Допускается вводить только буквы и цифры")
            logger.warning("%s Ошибка валидации логина при входе: %s" %(request.remote_addr,login))
            return render_template("login.html")
        if not validate(str(password)):
            flash("Допускается вводить только буквы и цифры")
            logger.warning("%s Ошибка валидации пароля при регистрации: %s" %(request.remote_addr,password))
            return render_template("login.html")
        row = models.getUser(username)
        arr = []
        if len(row)!=0:
            for i in row[0]:
                arr.append(i)
            if(password!=arr[2]):
                flash("Неверный пароль / логин")
                logger.warning("%s Введен неверный пароль: %s для пользователя: %s" %(request.remote_addr,password,username))
                return render_template("login.html")
            else:
                userlogin = UserLogin().create(arr[1])
                login_user(userlogin)
                flash("Успешный вход")
                logger.info("%s Успешный вход:%s:%s" %(request.remote_addr,username,password))
                content = {}
                content ['username'] = []
                content ['username'] = username
                is_admin = models.getUser(username)[0]
                data = {"user" : username, "password" : password, "is_admin" : is_admin[3], "comment": is_admin[4]}
                token = encodeJWT(data)
                response = make_response(render_template("status.html",workersAmount = models.getWorkersAmount('\'Head\''), headVagonStatus = models.getVagonStatus('\'Head\''), capitansList = models.getCapitansList(),timeToStation = getTime(),accountingStatus = models.getAccountingStatus("Accounting"), accountingVagonStatus = models.getVagonStatus('\'Accounting\''), cargoAmount= models.getAllCargoAmount(), cargoVagonStatus = models.getVagonStatus('\'Cargo\'')))
                response.set_cookie("jwt", token)
                return response
        else:
            flash("Неверный пароль / логин")
            logger.warning("%s Введен неверный пароль / логин: %s:%s" %(request.remote_addr,username,password))
            return render_template("login.html")

#@login_required
@app.route('/status', methods=['GET','POST'])
def status():
    if request.method == "GET":    
        return render_template("status.html", 
            workersAmount = models.getWorkersAmount('\'Head\''), 
            headVagonStatus = models.getVagonStatus('\'Head\''), 
            capitansList = models.getCapitansList(), 
            timeToStation = getTime(),
            accountingStatus = models.getAccountingStatus("Accounting"), 
            accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
            cargoAmount= models.getAllCargoAmount(), cargoVagonStatus = models.getVagonStatus('\'Cargo\'') )

#@login_required
@app.route('/accounting', methods=['GET','POST'])
def accounting():
    if request.method == "GET":
        username = ""
        user_comment = ""
        token_data = "None"
        userArray = models.getUsers()
        try:
            token = request.cookies.get("jwt")
            if token != None:
                token_data = decodeJWT(token)
                username = token_data['user']
                user_comment = models.selectUserComment("\'%s\'"%username)
                logger.info("%s Успешный вход в бухгалтерию: %s" %(request.remote_addr,token_data))
                logger.info("%s Пользователь %s получил свой комментарий" %(request.remote_addr, username))
            else:
                logger.warning("%s Попытка неавторизованного входа в Бухгалтерию:%s" %(request.remote_addr,token_data))
                flash ("Пользователь неавторизован")
        except Exception as err:
            
            print(err)
    return render_template("accounting.html",
         cargoAmountStatus = models.getAllCargoAmount(),
         headVagonStatus = models.getVagonStatus('\'Head\''), 
         accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
         cargoVagonStatus = models.getVagonStatus('\'Cargo\''), 
         humanTime = models.getWorkersAmount('\'Head\''),
         username = username, user_comment = user_comment, userArray = userArray)
            
    return render_template("accounting.html",
         cargoAmountStatus = models.getAllCargoAmount(),
         headVagonStatus = models.getVagonStatus('\'Head\''), 
         accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
         cargoVagonStatus = models.getVagonStatus('\'Cargo\''), 
         humanTime = models.getWorkersAmount('\'Head\''),
         username = username, user_comment = user_comment, userArray = userArray)
    if request.method == "POST":
        token = request.cookies.get("jwt")
        token_data = decodeJWT(token)
        userArray = models.getUsers()
        if request.form.get('updateHumanTimeInput') == 'Обновить данные':
            if token_data['is_admin'] == '1':
                if len(request.form['humanTimeInput']) == 0:
                    flash("Не указаны человекочасы")
                else:
                    out = request.form['humanTimeInput']
                    flash("Новое количество человекочасов:" + str(out))
                    models.updateWorkersAmount(out,'\'Head\'')
                    username = token_data['user']
                    user_comment = token_data['comment']
                    logger.info("%s Введены новые человекочасы: %s пользователем %s с комментарием %s" %(request.remote_addr, out,username,user_comment))
                    return render_template("accounting.html",
                        cargoAmountStatus = models.getAllCargoAmount(),
                        headVagonStatus = models.getVagonStatus('\'Head\''), 
                        accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
                        cargoVagonStatus = models.getVagonStatus('\'Cargo\''), 
                        humanTime = models.getWorkersAmount('\'Head\''),
                        username = username, user_comment = user_comment, userArray = userArray)
            else:
                flash('Только капитан может вносить изменения! Текущий пользователь:' + str(token_data))
                logger.warning("%s Попытка изменения человекочасов %s" %(request.remote_addr,token_data))
        if request.form.get('changeVagonStatusButton') == 'Принудительная уборка':
                workers = models.getWorkersAmount('\'Head\'')
                if workers > 0:
                    models.updateVagonStatus("True",'\'Head\'')
                    models.updateVagonStatus("True",'\'Accounting\'')
                    models.updateVagonStatus("True",'\'Cargo\'')
                    username = token_data['user']
                    user_comment = token_data['comment']
                    return render_template("accounting.html",cargoAmountStatus = models.getAllCargoAmount(),
                                                headVagonStatus = models.getVagonStatus('\'Head\''), 
                                                accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
                                                cargoVagonStatus = models.getVagonStatus('\'Cargo\''), 
                                                humanTime = models.getWorkersAmount('\'Head\''),
                                                username = username, user_comment = user_comment, userArray = userArray)
                else:
                    flash ("Нет человекочасов для уборки!")
        if request.form.get('userCommentInput') == 'Обновить комментарий':
            token = request.cookies.get("jwt")
            token_data = decodeJWT(token)
            username = token_data['user']
            user_comment = request.form['userComment']
            token_data['comment'] = user_comment
            models.updateUserComment(username,user_comment)
            token = encodeJWT(token_data)
            logger.info("%s Для пользователя %s изменен комментарий:%s" %(request.remote_addr, username,user_comment))
            response = make_response(render_template("accounting.html",cargoAmountStatus = models.getAllCargoAmount(),
                                                headVagonStatus = models.getVagonStatus('\'Head\''), 
                                                accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
                                                cargoVagonStatus = models.getVagonStatus('\'Cargo\''), 
                                                humanTime = models.getWorkersAmount('\'Head\''),
                                                username = username, user_comment = user_comment, userArray = userArray))
            response.set_cookie("jwt", token)
            return response
        if request.form.get('nominateCaptain') == 'Назначить капитаном':
            username = request.form.get('userSelect')
            user_comment = token_data['comment']
            if token_data["is_admin"] == '0':
                flash("Только капитан может назначать капитана")
                return render_template("accounting.html",cargoAmountStatus = models.getAllCargoAmount(),
                                                    headVagonStatus = models.getVagonStatus('\'Head\''), 
                                                    accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
                                                    cargoVagonStatus = models.getVagonStatus('\'Cargo\''), 
                                                    humanTime = models.getWorkersAmount('\'Head\''),
                                                    username = username, user_comment = user_comment, userArray = userArray)
            else:
                models.updateCaptain(username)
                flash("Пользователь %s назначен капитаном" %username)
                logger.warning("%s %s Стал капитаном" %(request.remote_addr,username))
                return render_template("accounting.html",cargoAmountStatus = models.getAllCargoAmount(),
                                                    headVagonStatus = models.getVagonStatus('\'Head\''), 
                                                    accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
                                                    cargoVagonStatus = models.getVagonStatus('\'Cargo\''), 
                                                    humanTime = models.getWorkersAmount('\'Head\''),
                                                    username = username, user_comment = user_comment, userArray = userArray)
            

    return render_template("accounting.html",
                        cargoAmountStatus = models.getAllCargoAmount(),
                        headVagonStatus = models.getVagonStatus('\'Head\''), 
                        accountingVagonStatus = models.getVagonStatus('\'Accounting\''), 
                        cargoVagonStatus = models.getVagonStatus('\'Cargo\''), 
                        humanTime = models.getWorkersAmount('\'Head\''))

@app.route('/cargo', methods=['GET','POST'])
def cargo():
    if request.method == "GET":
        return render_template("cargo.html", 
        cargoTypeArray = models.getCargoTypeArray(),
        cargoFoodType= models.getCargoType('\'Свинина\''), cargoFoodAmount = models.getCargoAmount('\'Мясо\''), cargoFoodStatus = models.getCargoStatus('\'Мясо\''), cargoFoodPass= models.getCargoPass('\'Мясо\''),
        cargoTechType= models.getCargoType('\'Инструменты\''), cargoTechAmount = models.getCargoAmount('\'Техника\''), cargoTechStatus = models.getCargoStatus('\'Техника\''),cargoTechPass = models.getCargoPass('\'Техника\''),
        cargoScienceType = models.getCargoType('\'Исследования\''),cargoScienceAmount= models.getCargoAmount('\'Наука\''), cargoScienceStatus= models.getCargoStatus('\'Наука\'') , cargoSciencePass= models.getCargoPass('\'Наука\''))
    if request.method == "POST":
        if request.form.get('cargoChangePassButton') == 'Сохранить пароль':
            if len(request.form['cargoChangePass']) == 0:
                flash("Введите пароль")
            else:
                passw = request.form['cargoChangePass']
                selectedName = request.form.get('cargoSelect')
                models.updateCargoPass(selectedName,passw)
                logger.info("%s Введен новый пароль: %s для груза: %s" %(request.remote_addr,passw,selectedName))
                flash("Пароль: "+ str(passw)+" сохранен для груза: " + str(selectedName))
            
        return render_template("cargo.html", 
        cargoTypeArray = models.getCargoTypeArray(),
        cargoFoodType= models.getCargoType('\'Свинина\''), cargoFoodAmount = models.getCargoAmount('\'Мясо\''), cargoFoodStatus = models.getCargoStatus('\'Мясо\''), cargoFoodPass= models.getCargoPass('\'Мясо\''),
        cargoTechType= models.getCargoType('\'Инструменты\''), cargoTechAmount = models.getCargoAmount('\'Техника\''), cargoTechStatus = models.getCargoStatus('\'Техника\''),cargoTechPass = models.getCargoPass('\'Техника\''),
        cargoScienceType = models.getCargoType('\'Исследования\''),cargoScienceAmount= models.getCargoAmount('\'Наука\''), cargoScienceStatus= models.getCargoStatus('\'Наука\'') , cargoSciencePass= models.getCargoPass('\'Наука\''))

        
@app.route('/station', methods=['GET','POST'])
def station():
    if request.method == "GET":      
        return render_template("station.html", timetotrain = getTime(), cargoVagonStatus=  models.getVagonStatus('\'Cargo\''),
        cargoFoodType= models.getCargoType('\'Свинина\''), cargoFoodAmount = models.getCargoAmount('\'Мясо\''), cargoFoodStatus = models.getCargoStatus('\'Мясо\''),
        cargoTechType= models.getCargoType('\'Инструменты\''), cargoTechAmount = models.getCargoAmount('\'Техника\''), cargoTechStatus = models.getCargoStatus('\'Техника\''),
        cargoScienceType = models.getCargoType('\'Исследования\''),cargoScienceAmount= models.getCargoAmount('\'Наука\''), cargoScienceStatus= models.getCargoStatus('\'Наука\'') ,
        cargoFoodNameArray = models.getCargoNameArray('\'Мясо\''),cargoTechNameArray = models.getCargoNameArray('\'Техника\''), cargoScienceNameArray = models.getCargoNameArray('\'Наука\''), AddedCargoTypeArray = models.getCargoTypeArray())
    if request.method == "POST":
        types = []
        if request.form.get('AddCargoButton') == 'AddCargoButton':
            selectedType = request.form.get('AddedCargoTypeArrayDropdown')
            cargoName = request.form['AddedCargoName']
            cargoAmount = request.form['AddedCargoAmount']
            cargoComment = request.form['AddedCommentCargoSteal']
            cargoPass = models.getCargoPass('\'%s\'' %selectedType)
            models.insertCargo(selectedType,cargoName,cargoAmount,cargoPass,cargoComment)
            logger.info("%s Добавлен новый груз: Тип %s, Имя %s, Количество %s, Пароль %s, Комментарий %s" %(request.remote_addr,selectedType,cargoName,cargoAmount,cargoPass,cargoComment))
            return render_template("station.html", timetotrain = getTime(), cargoVagonStatus=  models.getVagonStatus('\'Cargo\''),
        cargoFoodType= models.getCargoType('\'Свинина\''), cargoFoodAmount = models.getCargoAmount('\'Мясо\''), cargoFoodStatus = models.getCargoStatus('\'Мясо\''),
        cargoTechType= models.getCargoType('\'Инструменты\''), cargoTechAmount = models.getCargoAmount('\'Техника\''), cargoTechStatus = models.getCargoStatus('\'Техника\''),
        cargoScienceType = models.getCargoType('\'Исследования\''),cargoScienceAmount= models.getCargoAmount('\'Наука\''), cargoScienceStatus= models.getCargoStatus('\'Наука\''),
        cargoFoodNameArray = models.getCargoNameArray('\'Мясо\''),cargoTechNameArray = models.getCargoNameArray('\'Техника\''), cargoScienceNameArray = models.getCargoNameArray('\'Наука\''), AddedCargoTypeArray = models.getCargoTypeArray())

        if request.form.get('ScienceSteal') == 'ScienceSteal':
            rightpass = models.getCargoPass('\'Наука\'')
            userpass = request.form['passScienceSteal']

            if rightpass == userpass:
                models.updateCargoStatus('\'Наука\'')
                cargoName = request.form.get('cargoScienceName')
                cargoComment = models.getCargoComment(cargoName)
                flash(cargoComment)
                logger.info("%s Для груза %s показан комментарий %s" %(request.remote_addr,cargoName,cargoComment))
                logger.warning("%s Груз Наука Украден! Введенный пароль: %s" %(request.remote_addr,userpass))

                return render_template("station.html", timetotrain = getTime(), cargoVagonStatus=  models.getVagonStatus('\'Cargo\''),
        cargoFoodType= models.getCargoType('\'Свинина\''), cargoFoodAmount = models.getCargoAmount('\'Мясо\''), cargoFoodStatus = models.getCargoStatus('\'Мясо\''),
        cargoTechType= models.getCargoType('\'Инструменты\''), cargoTechAmount = models.getCargoAmount('\'Техника\''), cargoTechStatus = models.getCargoStatus('\'Техника\''),
        cargoScienceType = models.getCargoType('\'Исследования\''),cargoScienceAmount= models.getCargoAmount('\'Наука\''), cargoScienceStatus= models.getCargoStatus('\'Наука\''),
        cargoFoodNameArray = models.getCargoNameArray('\'Мясо\''),cargoTechNameArray = models.getCargoNameArray('\'Техника\''), cargoScienceNameArray = models.getCargoNameArray('\'Наука\''), AddedCargoTypeArray = models.getCargoTypeArray())
            else:
                logger.warning("%s Введен неверный пароль для груза:%s" %(request.remote_addr,userpass))
                flash('Неверный пароль!')
            
        if request.form.get('TechSteal') == 'TechSteal':
            rightpass = models.getCargoPass('\'Техника\'')
            userpass = request.form['passTechSteal']
            if rightpass == userpass:
                models.updateCargoStatus('\'Техника\'')
                flash('Груз украден!')
                logger.warning("%s Груз Техника Украден! Введенный пароль: %s" %(request.remote_addr,userpass))
                return render_template("station.html", timetotrain = getTime(), cargoVagonStatus=  models.getVagonStatus('\'Cargo\''),
        cargoFoodType= models.getCargoType('\'Свинина\''), cargoFoodAmount = models.getCargoAmount('\'Мясо\''), cargoFoodStatus = models.getCargoStatus('\'Мясо\''),
        cargoTechType= models.getCargoType('\'Инструменты\''), cargoTechAmount = models.getCargoAmount('\'Техника\''), cargoTechStatus = models.getCargoStatus('\'Техника\''),
        cargoScienceType = models.getCargoType('\'Исследования\''),cargoScienceAmount= models.getCargoAmount('\'Наука\''), cargoScienceStatus= models.getCargoStatus('\'Наука\''),
        cargoFoodNameArray = models.getCargoNameArray('\'Мясо\''),cargoTechNameArray = models.getCargoNameArray('\'Техника\''), cargoScienceNameArray = models.getCargoNameArray('\'Наука\''), AddedCargoTypeArray = models.getCargoTypeArray())
            else:
                logger.warning("%s Введен неверный пароль %s для груза Техника" %(request.remote_addr,userpass))
                flash("Неверный пароль!")

        if request.form.get('FoodSteal') == 'FoodSteal':
            rightpass = models.getCargoPass('\'Мясо\'')
            userpass = request.form['passFoodSteal']
            if rightpass == userpass:
                models.updateCargoStatus('\'Мясо\'')
                flash('Груз украден!')
                logger.warning("%s Груз Мясо Украден! Введенный пароль: %s" %(request.remote_addr,userpass))
                return render_template("station.html", timetotrain = getTime(), cargoVagonStatus=  models.getVagonStatus('\'Cargo\''),
        cargoFoodType= models.getCargoType('\'Свинина\''), cargoFoodAmount = models.getCargoAmount('\'Мясо\''), cargoFoodStatus = models.getCargoStatus('\'Мясо\''),
        cargoTechType= models.getCargoType('\'Инструменты\''), cargoTechAmount = models.getCargoAmount('\'Техника\''), cargoTechStatus = models.getCargoStatus('\'Техника\''),
        cargoScienceType = models.getCargoType('\'Исследования\''),cargoScienceAmount= models.getCargoAmount('\'Наука\''), cargoScienceStatus= models.getCargoStatus('\'Наука\''),
        cargoFoodNameArray = models.getCargoNameArray('\'Мясо\''),cargoTechNameArray = models.getCargoNameArray('\'Техника\''), cargoScienceNameArray = models.getCargoNameArray('\'Наука\''), AddedCargoTypeArray = models.getCargoTypeArray())
            else:
                flash("Неверный пароль!") 
                logger.warning("%s Введен неверный пароль %s для груза Мясо" %(request.remote_addr,userpass))  
        return render_template("station.html", timetotrain = getTime(), cargoVagonStatus=  models.getVagonStatus('\'Cargo\''),
        cargoFoodType= models.getCargoType('\'Свинина\''), cargoFoodAmount = models.getCargoAmount('\'Мясо\''), cargoFoodStatus = models.getCargoStatus('\'Мясо\''),
        cargoTechType= models.getCargoType('\'Инструменты\''), cargoTechAmount = models.getCargoAmount('\'Техника\''), cargoTechStatus = models.getCargoStatus('\'Техника\''),
        cargoScienceType = models.getCargoType('\'Исследования\''),cargoScienceAmount= models.getCargoAmount('\'Наука\''), cargoScienceStatus= models.getCargoStatus('\'Наука\''),
        cargoFoodNameArray = models.getCargoNameArray('\'Мясо\''),cargoTechNameArray = models.getCargoNameArray('\'Техника\''), cargoScienceNameArray = models.getCargoNameArray('\'Наука\''), AddedCargoTypeArray = models.getCargoTypeArray())
    
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(userlogin):
    return UserLogin().fromDB(userlogin)

def getTime():
    t = datetime.now()
    time = t.strftime("%M")

    if int(time)%30 == 0:
        num = randint(1,3)
        if num == 1:
            models.updateVagonStatus("False",'\'Head\'')
        elif num == 2:    
            models.updateVagonStatus("False",'\'Accounting\'')
        else:
            models.updateVagonStatus("False",'\'Cargo\'')

    if int(time)%3 == 0:
        models.renewCargo()
        logger.info("Поезд прибыл, товары в наличии")
        return 'Поезд прибыл'
    else:
        out = 3 - int(time)%3 
        return out

class UserLogin():
    def fromDB(self,user):  
        self.__user = models.getUserID(user)
        return self
    def create (self,user):
        self.__user=user
        return self
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        out = ""
        id = models.getUserID(self.__user)
        if len(id)!=0:
            for i in id:
                out = i
                break
            return out[0]
        else:
            return NULL



#регулярка
def validate(s):
    regex = re.compile(r'^[a-zA-Z0-9]+$')
    a = regex.match(str(s))
    if a !=None:
        return True
    else:
        return False

def encodeJWT(data):
    token = ""
    token = jwt.encode(data, "secret")
    return token.decode('UTF-8')

def decodeJWT(token):
    data = jwt.decode(token, "secret", algorithms=["HS256"], verify=False)
    return data

if __name__ == '__main__':
    models.createDB()
    app.run(debug=False, port = 11000, host='0.0.0.0')
