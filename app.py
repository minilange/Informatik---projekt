
import sqlite3 as SQL
from tokenize import String
from flask import Flask, redirect, render_template, request, session
from flask_session.__init__ import Session
# from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

print("Opened database")

# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response

@app.route("/")
def index():
    data = dbCall("SELECT * FROM users")
    print(f"table: {data}")
    # print(f"session: {session['test']}")    
    return render_template("index.html", data=data)

@app.route("/about")
def about():
    return render_template("about.html")

def dbCall(query):    
    conn = SQL.connect("shop.db", check_same_thread=False)
    db = conn.cursor()

    data = db.execute(query).fetchall()
    newData = []
    for row in data:
        tmp = []
        for atr in row:
            tmp.append(atr)
            
        newData.append(tmp)
    db.close()
    return newData  
