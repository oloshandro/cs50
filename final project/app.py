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

# CURRENCIES = ["US dollar (USD)", "Euro (EUR)", "Ukrainian hryvnia (UAH)", "Polish zloty (PLN)", "Pound sterling (GBP)"]
# CURRENCY_symbol = ["$", "€", "₴", "zł", "£"]

CURRENCIES = {
    "US dollar (USD)":"$", 
    "Euro (EUR)":"$", 
    "Ukrainian hryvnia (UAH)":"₴",
    "Polish zloty (PLN)":"zł",
    "Pound sterling (GBP)":"£"
    }


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
    return render_template("expenses.html")


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

        CATEGORIES = ['Housing', 'Transport', 'Food', 'Shopping', 'Utilities', 'Insurance', 'Healthcare', 'Taxes', 'Eating out', 'Leisure', 'Sport', 'Pets', 'Learning', 'Salary', 'Charity']
        for cat in CATEGORIES:
            db.execute("INSERT INTO categories (user_id, category) VALUES (:user_id, :category)",
                user_id=session["user_id"], category=cat)

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
    rows = db.execute("SELECT account_name, currency, balance, currency_symbol FROM accounts WHERE user_id= :user_id", user_id=session["user_id"])
        
    # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    accounts = []
    for row in rows:
        # create a list with all the info about the stock and append it to a list of every stock owned by the user
        accounts.append(list((row['account_name'], row['currency'], row['balance'], row['currency_symbol'])))
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
            db.execute("INSERT INTO accounts (user_id, account_name, currency, balance, currency_symbol) VALUES (:user_id, :account_name, :currency, :balance, :currency_symbol)",
                            user_id=session["user_id"], account_name=account_name, currency=currency, balance=balance, currency_symbol=CURRENCIES[currency])

        return render_template("account.html", accounts=accounts, currencies=CURRENCIES, message="You've created a new account")
       

    #User reached route via GET
    else:
        return render_template("account.html", accounts=accounts , currencies=CURRENCIES)



@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():

    """show categories or create a new category"""
    # query existing categories    
    rows = db.execute("SELECT category FROM categories WHERE user_id= :user_id", user_id=session["user_id"])
        
    # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    categories = []
    for row in rows:
        # create a list with all the info about the stock and append it to a list of every stock owned by the user
        categories.append(row['category'])


    # creating new account via POST to /quote and validating the fields 'name', 'currency', 'balance'
    if request.method == "POST":
        new_category = request.form.get("new_category")

        if not new_category or new_category in CATEGORIES:
            return render_template("categories.html", message="Please, create a name category")

         # insert new category into the categories table
        if new_category not in CATEGORIES:
            db.execute("INSERT INTO categories (user_id, category) VALUES (:user_id, :category)",
                            user_id=session["user_id"], category=new_category)

        return render_template("categories.html", message="You've added new category")


    #User reached route via GET
    else:
        return render_template("categories.html", categories=categories)




@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    """navigate through user accounts or create a new account"""
    # query all users categories from 'transactions' table for account_name total balance 
    # rows = db.execute("SELECT category, category_balance FROM categories WHERE user_id= :user_id", user_id=session["user_id"])
        
    # # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    # # categories = []
    # for row in rows:
    #     # create a list with all the info about the categories and append it to a list of every category and amount of money spent
    #     categories.append(list((row['category'], row['category_balance'])))
    
    
    # render_template("expenses.html", categories=categories)
    rows = db.execute("SELECT category FROM categories WHERE user_id=:user_id",
                    user_id=session["user_id"])

    categories = []
    for row in rows:
        categories.append(row['category'])


    row_accounts = db.execute("SELECT account_name, balance, currency_symbol FROM accounts WHERE user_id= :user_id", user_id=session["user_id"])
    accounts = []
    for row in row_accounts:
        accounts.append(list((row['account_name'], row['balance'], row['currency_symbol'])))


    # creating new expense via POST to /expenses and validating the fields 'category', 'account_name', 'currency', 'balance'
    if request.method == "POST":
        category = request.form.get("category")
        description = request.form.get("description")
        account_name = request.form.get("account_name")
        amount = int(request.form.get("amount"))

        if not category or category not in categories:
            return render_template("expenses.html", categories=categories, accounts=accounts, message="Please, choose the category from the list")

        if not account_name:
            return render_template("expenses.html", categories=categories, accounts=accounts, message="Please, choose one of the accounts you have")
        
        if not amount:
            return render_template("expenses.html", categories=categories, accounts=accounts, message="Please, add the amount money spent")

        if not description:
            return render_template("expenses.html", categories=categories, accounts=accounts)
        

        # # check if there is enough money on the account
        # account_balance = db.execute("SELECT balance FROM accounts WHERE user_id= :user_id", user_id=session["user_id"])
        # if amount > account_balance:
        #     return render_template("expenses.html", categories=CATEGORIES, accounts=accounts, message="Not enough money on this account. Please, choose anouther account")

        # # update total expense balance of the category
        # if category not in row['category']:
        #     db.execute("INSERT INRO categories (user_id, category, category_balance) VALUES (:user_id, :category, :category_balance)",
        #                     user_id=session["user_id"], category=category, category_balance=amount)
        
        
        # else:
        #     category_balance += row['category_balance']
        #     db.execute("UPDATE categories SET category_balance= :category_balance WHERE user_id= :user_id",
        #                     category_balance=category_balance, user_id=session["user_id"])


        # insert new category into the transactions table
        transaction_date = str(datetime.now())[0:10]
        db.execute("INSERT INTO transactions (user_id, category, account_name, description, amount, transaction_date) VALUES (:user_id, :category, :account_name, :description, :amount, :transaction_date)",
                            user_id=session["user_id"], category=category, account_name=account_name, description=description, amount=-amount, transaction_date=transaction_date)
        
        
        # update current balance of the account
        current_balance = 0
        for acc in accounts:
            if acc[0] == account_name:
                current_balance = acc[1]
                break

        new_balance = current_balance - amount

        db.execute("UPDATE accounts SET balance= :new_balance WHERE user_id= :user_id AND account_name= :account_name ", 
                        new_balance=new_balance, user_id=session["user_id"], account_name=account_name)

        return render_template("expenses.html", categories=categories, accounts=accounts, message="You've added a new expense")
       

    #User reached route via GET
    else:
        return render_template("expenses.html", categories=categories, accounts=accounts)



@app.route("/income", methods=["GET", "POST"])
@login_required
def income():
    """navigate through user accounts or create a new account"""
    # query all users categories from 'transactions' table for account_name total balance 
    # rows = db.execute("SELECT category, category_balance FROM categories WHERE user_id= :user_id", user_id=session["user_id"])
        
    # # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    # # categories = []
    # for row in rows:
    #     # create a list with all the info about the categories and append it to a list of every category and amount of money spent
    #     categories.append(list((row['category'], row['category_balance'])))
    
    
    # render_template("expenses.html", categories=categories)
    rows = db.execute("SELECT category FROM categories WHERE user_id=:user_id",
                    user_id=session["user_id"])

    categories = []
    for row in rows:
        categories.append(row['category'])

    
    row_accounts = db.execute("SELECT account_name, balance FROM accounts WHERE user_id= :user_id", user_id=session["user_id"])
    accounts = []
    for row in row_accounts:
        accounts.append(list((row['account_name'], row['balance'])))


    # creating new expense via POST to /expenses and validating the fields 'category', 'account_name', 'currency', 'balance'
    if request.method == "POST":
        category = request.form.get("category")
        account_name = request.form.get("account_name")
        description = request.form.get("description")
        amount = int(request.form.get("amount"))

        if not category or category not in categories:
            return render_template("income.html", categories=categories, accounts=accounts, message="Please, choose the category from the list")

        if not account_name:
            return render_template("income.html", categories=categories, accounts=accounts, message="Please, choose one of the accounts you have")
        
        if not amount:
            return render_template("income.html", categories=categories, accounts=accounts, message="Please, add the amount money earned")

        # if not description:
        #     return render_template("income.html", categories=categories, accounts=accounts)

        # insert new category into the transactions table
        transaction_date = str(datetime.now())[0:10]
        db.execute("INSERT INTO transactions (user_id, category, account_name, description, amount, transaction_date) VALUES (:user_id, :category, :account_name, :description, :amount, :transaction_date)",
                            user_id=session["user_id"], category=category, account_name=account_name, description=description, amount=+amount, transaction_date=transaction_date)
        
        
        # update current balance of the account
        current_balance = 0
        for acc in accounts:
            if acc[0] == account_name:
                current_balance = acc[1]
                break

        new_balance = current_balance + amount

        db.execute("UPDATE accounts SET balance= :new_balance WHERE user_id= :user_id AND account_name= :account_name ", 
                        new_balance=new_balance, user_id=session["user_id"], account_name=account_name)

        return render_template("income.html", categories=categories, accounts=accounts, message="You've added new income")
       

    #User reached route via GET
    else:
        return render_template("income.html", categories=categories, accounts=accounts)


@app.route("/transactions")
@login_required
def transactions():
    """Show history of transactions"""
    # get info from transactions database
    rows = db.execute("SELECT * FROM transactions WHERE user_id = ?",
                            session["user_id"])

    # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    transactions = []
    for row in rows:
        # create a list with all the info about the stock and append it to a list of every stock owned by the user
        transactions.append(list((row['account_name'],  row['category'],  row['amount'],  row['description'], row['transaction_date'])))
    transactions.reverse()
    return render_template("transactions.html", transactions=transactions)










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

