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
import os
import logging
import sys
# enabling print statements
sys.stdout.flush()# TODO: CLeanup import statements
# TODO: CONN.CLOSE?!?!
# TODO: DELETE DUPLICATE PROJECTS
# TODO: FLASH FOR INCORRECT PASSWORDS/USERNAME, ETC
# TODO: ADD THIS FEATURE??
# number of projects to display per row
# TODO: STILL OCCASIONALLY DISPLAY 8/9 PROJECTS
# TODO: ADD TRY/CATCHES TO EVERY c.execute!!
# TODO: MORE IN SYNC TITLES BETWEEN THE SPIDERS ITEMS AND THE TABLE!!!
#   (EX: url vs project_url)
PROJECTS_PER_ROW = 3

# -----------------------------database creation--------------------------------
# https://docs.python.org/3.6/library/sqlite3.html#sqlite3.Connection
# create a Connection object that represents the database.
conn = sqlite3.connect("DIYnow.db")

# http://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
# https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
conn.row_factory = sqlite3.Row

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


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    """Show new projects and allow user to add projects to their list"""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        user_id = session["user_id"]

        # get which project the user selected
        project_url = request.form["DIYnow"]

        json_data=open("ProjectOut.json").read()
        projects = json.loads(json_data)

        # http://stackoverflow.com/questions/19794695/flask-python-buttons
        for project in projects:
            if project["url"] == project_url:
                project_url = project["url"]
                project_name = project["title"]
                image_url = project["image_url"]

        # insert the new project into the portfolio table
        try:
            c.execute("INSERT INTO projects (id, project_url, project_name, image_url) VALUES(:id, :project_url, :project_name, :image_url)",
                            {"id" : user_id, "project_url" : project_url, "project_name" : project_name, "image_url" : image_url })
            conn.commit()

        except RuntimeError:
            return ("ERROR updated too few or too many rows of projects")
        # unique index (user_project) prevents duplicate addition of projects
        # http://stackoverflow.com/questions/29312882/sqlite-preventing-duplicate-rows
        except sqlite3.IntegrityError:
            return ("you've already added that project!")

        flash("Added!")
        return render_template("home.html", projects = projects)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
    # http://stackoverflow.com/questions/36384286/how-to-integrate-flask-scrapy
        if (os.path.isfile('ProjectOut.json')):
            os.remove("ProjectOut.json")

        projectSpiderName = "Projects"
        subprocess.check_output(['scrapy', 'crawl', projectSpiderName, "-o", "ProjectOut.json"])
        json_data=open("ProjectOut.json").read()
        projects = json.loads(json_data)
        return render_template("home.html", projects = projects)

# CREDIT PSET 7
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return ("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password")

        # query database for username
        c.execute("SELECT * FROM users WHERE username = :username", {"username":request.form.get("username")})
        rows = c.fetchall()

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return ("invalid username and/or password")
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("my_projects"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # ensure username was submitted
        username = request.form.get("username")
        if not username:
            return ("must provide username")

        # ensure username is unique
        if c.execute("SELECT username FROM users WHERE username = :username", {"username" : username}).fetchall() != []:
            return ("must provide unique username")

        # ensure password was submitted
        password = request.form.get("password")
        if not password:
            flash("Must provide password")
            return render_template("register.html")

        # ensure password was confirmed correctly
        if request.form.get("confirm_password") != password:
            return ("incorrect password confirmation")

        # encrypt user's password and insert user info into users table
        try:
            c.execute("INSERT INTO users (username, hash) VALUES(:username, :hash_)",
                        {"username" : username, "hash_" : pwd_context.encrypt(password)})
            c.execute("SELECT id FROM users WHERE username = :username", {"username":request.form.get("username")})
            new_id = c.fetchone()
            # save the changes to the table
            conn.commit()

        except RuntimeError:
            return ("ERROR creating new user")

        # remember which user has logged in, redirect to index page and welcome
        session["user_id"] = new_id["id"]

        flash("Registered!")
        return redirect(url_for("home"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def my_projects():
    """Get all of user's favorited projects"""
    # get all user's selections from projects
    user_id = session["user_id"]
    if request.method == "POST":

        # get which number the user selected
        project_url = request.form["Delete"]

        c.execute("SELECT project_url, project_name, image_url FROM projects WHERE id = :user_id", {"user_id" : user_id})
        all_projects = c.fetchall()

        for project in all_projects:
            if project["project_url"] == project_url:
                project_url = project["project_url"]

        try:
            c.execute("DELETE FROM projects WHERE id = :user_id AND project_url = :project_url", {"user_id" : user_id, "project_url" : project_url})
            conn.commit()

        except RuntimeError:
            return("ERROR Deleting project")

        flash("Deleted!")
        c.execute("SELECT project_url, project_name, image_url FROM projects WHERE id = :user_id", {"user_id" : user_id})
        all_projects = c.fetchall()
        return render_template("my_projects.html", projects = all_projects)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        c.execute("SELECT project_url, project_name, image_url FROM projects WHERE id = :user_id", {"user_id" : user_id})
        all_projects = c.fetchall()

        return render_template("my_projects.html", projects = all_projects)


# # We can also close the connection if we are done with it.
# # Just be sure any changes have been committed or they will be lost.
# conn.close()
