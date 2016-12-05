from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from datetime import datetime
from time import gmtime, strftime
import sqlite3
import hashlib
import subprocess
import json
from helpers import *
# number of projects to display per row
PROJECTS_PER_ROW = 3

# -----------------------------database creation--------------------------------
# https://docs.python.org/3.6/library/sqlite3.html#sqlite3.Connection
# create a Connection object that represents the database.
conn = sqlite3.connect("DIYnow.db")

# creating a cursor object for executing SQL commands
c = conn.cursor()



# ---------------------------------flask setup----------------------------------
# configure application
app = Flask(__name__)

# ensure responses aren't cached
# CREDIT PSET7
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# export FLASK_APP=application.py
# ---------------------------------END SETUP------------------------------------

@app.route("/")
#@login_required
def index():
	# http://stackoverflow.com/questions/36384286/how-to-integrate-flask-scrapy
	projectSpiderName = "Projects"
	subprocess.check_output(['scrapy', 'crawl', projectSpiderName, "-o", "ProjectOut.json"])
	json_data=open("ProjectOut.json").read()
	projects = json.loads(json_data)

	return render_template("index.html", projects = projects)


@app.route("/login", methods=["GET", "POST"])
def login():
	return render_template("index.html");

# # Create table
# c.execute('''CREATE TABLE stocks
#              (date text, trans text, symbol text, qty real, price real)''')

# # Insert a row of data
# c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

# # Save (commit) the changes
# conn.commit()

# # We can also close the connection if we are done with it.
# # Just be sure any changes have been committed or they will be lost.
# conn.close()
