import uuid
from flask import Flask, render_template, has_request_context, request, redirect #url_for, flash
from model import *

# main
app = Flask(__name__)



@app.route("/", methods = ['GET', 'POST'] )
def start():        
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST' and request.form.get("book"):    
        create_table()
        id = uuid.uuid4()
        name = request.form.get("name")
        city = request.form.get("city")
        place = request.form.get("place")
        vanNumber = request.form.get("vanNumber")
        cardID = request.form.get("cardID")
        book(id, name, city, place, vanNumber, cardID)                
        return render_template('book.html', book_id=id)
    elif request.method == "POST" and  request.form.get("check"):
        elements = check(request.form.get("book_id").lower())
        return render_template('check.html', elements=elements)
        
if __name__ == '__main__':
    app.run(debug = False, host='0.0.0.0', port=10000)