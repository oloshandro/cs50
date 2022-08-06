from locale import currency
import os
import re
from sre_parse import CATEGORIES

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, time, timezone

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///MyMoney.db")

CURRENCIES = ["US dollar (USD)", "Euro (EUR)", "Ukrainian hryvnia (UAH)", "Polish zloty (PLN)"]
CATEGORIES = ['Housing', 'Transport', 'Food', 'Utilities', 'Insurance', 'Healthcare', 'Taxes', 'Eating out', 'Leisure', 'Sport', 'Pets', 'Learning', 'Salary']



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show logged in main page"""
    # show currect balance + accounts, categories, transactions, overview buttons
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return render_template("login.html", message="Please, provide your email")
            # flash("Please, provide your email")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", message="Please, provide your password")
            # return apology("Please, provide your password")
            # flash("Please, provide your password")

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", message="invalid username and/or password")
            # return apology("invalid username and/or password")
            # flash("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # validate  email was filled in properly + email as input with ReGex
        email = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if not re.match(email, request.form.get("email")) or not request.form.get("email"):
            return render_template("register.html", message="Please, enter your email")


        # Ensure password was created
        elif not request.form.get("password"):
            return render_template("register.html", message="Please, create pasword")

        # Ensure confirm password matches is correct
        elif request.form.get("password") != request.form.get("confirmation"):
            # flash("password")
            return render_template("register.html", message="Passwords don't match")


        # query database if the user with this email already exists
        elif db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email")):
            # return render_template("apology.html")
            return render_template("register.html", message="User with such email already exists")


        # INSERT the new user into users, storing a hash username, password
        db.execute("INSERT INTO users (email, hash) VALUES(:email, :hash)",
            email=request.form.get("email"), hash=generate_password_hash(request.form.get("password")))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # ??Redirect user to home page
        return redirect("/")

    #User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """navigate through user accounts or create a new account"""
    # query all users acounts from 'accounts' db
    rows = db.execute("SELECT account_name, currency, balance FROM accounts WHERE user_id= :user_id", user_id=session["user_id"])
        
    # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    accounts = []
    for row in rows:
        # create a list with all the info about the stock and append it to a list of every stock owned by the user
        accounts.append(list((row['account_name'], row['currency'], row['balance'])))
    # render_template("account.html", accounts=accounts)


    # creating new account via POST to /quote and validating the fields 'name', 'currency', 'balance'
    if request.method == "POST":
        account_name = request.form.get("account_name")
        currency = request.form.get("currency")
        balance = request.form.get("balance")

        if not account_name:
            return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="Please, create a name for your account")
        
        if not currency or currency not in CURRENCIES:
            return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="Please, choose the currency from the field")

        if not balance or balance.isdigit == False:
            return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="Please, add the current balance")

        # insert new account into the accounts table
        if account_name not in accounts:
            db.execute("INSERT INTO accounts (user_id, account_name, currency, balance) VALUES (:user_id, :account_name, :currency, :balance)",
                            user_id=session["user_id"], account_name=account_name, currency=currency, balance=balance)

        return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="You've created a new account")
       

    #User reached route via GET
    else:
        return render_template("account.html", accounts=accounts , currencies=CURRENCIES)









@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """navigate through user accounts or create a new account"""
    # query all users acounts from 'accounts' db
    rows = db.execute("SELECT account_name, currency, balance FROM accounts WHERE user_id= :user_id", user_id=session["user_id"])
        
    # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    accounts = []
    for row in rows:
        # create a list with all the info about the stock and append it to a list of every stock owned by the user
        accounts.append(list((row['account_name'], row['currency'], row['balance'])))
    # render_template("account.html", accounts=accounts)


    # creating new account via POST to /quote and validating the fields 'name', 'currency', 'balance'
    if request.method == "POST":
        account_name = request.form.get("account_name")
        currency = request.form.get("currency")
        balance = request.form.get("balance")

        if not account_name:
            return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="Please, create a name for your account")
        
        if not currency or currency not in CURRENCIES:
            return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="Please, choose the currency from the field")

        if not balance or balance.isdigit == False:
            return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="Please, add the current balance")

        # insert new account into the accounts table
        if account_name not in accounts:
            db.execute("INSERT INTO accounts (user_id, account_name, currency, balance) VALUES (:user_id, :account_name, :currency, :balance)",
                            user_id=session["user_id"], account_name=account_name, currency=currency, balance=balance)

        return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="You've created a new account")
       

    #User reached route via GET
    else:
        return render_template("account.html", accounts=accounts , currencies=CURRENCIES)









# @app.route("/account", methods=["GET", "POST"])
# @login_required
# def create_account(): 
#     # creating new account via POST to /quote and validating the fields 'name', 'currency', 'balance'
#     if request.method == "POST":
#         if not request.form.get("name"):
#             return render_template("account.html", message="Please, create a name for your account")
        
#         elif not request.form.get("currency") or request.form.get("currency") not in CURRENCIES:
#             return render_template("account.html", message="Please, choose the currency from the field")

#         elif not request.form.get("balance") or request.form.get("balance").isdigit == False:
#              return render_template("account.html", message="Please, add the current balance")


#      #User reached route via GET
#     else:
#         return render_template("account.html", currencies=CURRENCIES)

