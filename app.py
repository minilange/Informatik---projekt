
import sqlite3 as SQL
from flask import Flask, redirect, render_template, request, session
# from flask_session import Session
# from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# app.config["TEMPLATES_AUTO_RELOAD"] = True

# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

con = SQL.connect("shop.db")
db = con.cursor()

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    # return redirect("templates/index.html")
    return render_template("index.html")