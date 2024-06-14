from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import apology, login_required, usd, is_float
from getprice import getprice
from linenotify import send_line_notify
import sqlite3


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# use SQLite database
connection = sqlite3.connect("icrypto.db", check_same_thread=False)
# datarow return as dict
connection.row_factory = sqlite3.Row
db = connection.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    userid = session["user_id"]
    rows = db.execute(
        "SELECT * FROM asset WHERE userid =?", (userid,)
    ).fetchall()
    asset_chg = 0
    origin = 0
    now_all = 0
    portfolio = []
    for row in rows:
        portfolio.append(dict(row))
    for item in portfolio:
        item["price"] = getprice(item["symbol"])
        item["chg"] = item["price"] - item["crpt_value"]
        item["total"] = item["price"] * item["amount"]
        now_all = now_all + item["total"]
        origin = origin + (item["crpt_value"] * item["amount"])
    
    asset_chg = now_all - origin
    if asset_chg > 0:
        color = "text-success"
    else:
        color = "text-danger"
        
    return render_template("index.html", rows=portfolio, all=now_all, change=asset_chg, color=color)

@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("missing symbol", "/deposit", 400)

        elif getprice(request.form.get("symbol")) == None:
            return apology("invalid symbol", "/deposit", 400)

        elif not request.form.get("amount"):
            return apology("missing amount", "/deposit", 400)

        elif not is_float(request.form.get("amount")) or float(request.form.get("amount")) < 0:
            return apology("invalid amount", "/deposit", 400)
        
        elif not request.form.get("crpt_value"):
            return apology("missing value", "/deposit", 400)

        elif not is_float(request.form.get("crpt_value")) or float(request.form.get("crpt_value")) < 0:
            return apology("invalid value", "/deposit", 400)

        symbol = request.form.get("symbol").upper()
        d_amount = float(request.form.get("amount"))
        d_crpt_value = float(request.form.get("crpt_value"))
        userid = session["user_id"]
        # Append new record in history
        db.execute(
            "INSERT INTO history (userid, symbol, amount, crpt_value, transc_time) VALUES (?, ?, ?, ?, datetime('now', '+8 hours'))", (userid, symbol, d_amount, d_crpt_value)
            )
        connection.commit()
        # Check if user is a holder
        asset = db.execute(
            "SELECT * FROM asset WHERE userid =? AND symbol =?", (userid, symbol)
            ).fetchall()

        if len(asset) != 1:
            db.execute(
                "INSERT INTO asset (userid, symbol, amount, crpt_value) VALUES (?, ?, ?, ?)", (userid, symbol, d_amount, d_crpt_value)
                )
            connection.commit()
        else:
            amount = d_amount + asset[0]["amount"]
            crpt_value = ((asset[0]["amount"] * asset[0]["crpt_value"]) + (d_amount * d_crpt_value)) / amount
            db.execute(
                "UPDATE asset SET amount = ?, crpt_value = ? WHERE userid =? AND symbol =?", (amount, crpt_value, userid, symbol)
                )
            connection.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("deposit.html")

@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("missing symbol", "/withdraw", 400)

        elif not request.form.get("amount"):
            return apology("missing amount", "/withdraw", 400)

        elif not is_float(request.form.get("amount")) or float(request.form.get("amount")) < 0:
            return apology("invalid amount", "/withdraw", 400)

        symbol = request.form.get("symbol").upper()
        w_amount = -float(request.form.get("amount"))
        userid = session["user_id"]
        
        # Check if amount is enough
        asset = db.execute(
            "SELECT * FROM asset WHERE userid =? AND symbol =?", (userid, symbol)
            ).fetchall()

        if len(asset) != 1:
            return apology("invalid symbol", "/withdraw", 400)
        
        amount = w_amount + asset[0]["amount"]

        if amount < 0:
            return apology("invalid amonunt", "/withdraw", 400)        
        else:
            # Append new record in history
            db.execute(
                "INSERT INTO history (userid, symbol, amount, transc_time) VALUES (?, ?, ?, datetime('now', '+8 hours'))", (userid, symbol, w_amount)
                )
            connection.commit()
            if amount == 0:
                db.execute(
                    "DELETE FROM asset WHERE userid =? AND symbol =?", (userid, symbol)
                )
                connection.commit()
            else:
                db.execute(
                    "UPDATE asset SET amount = ? WHERE userid =? AND symbol =?", (amount, userid, symbol)
                )
                connection.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        userid = session["user_id"]
        row = db.execute(
            "SELECT * FROM asset WHERE userid =?", (userid,)
        ).fetchall()
        return render_template("withdraw.html", rows=row)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    userid = session["user_id"]
    row = db.execute(
        "SELECT * FROM history WHERE userid =? ORDER BY transc_time DESC", (userid,)
    ).fetchall()
    return render_template("history.html", rows=row)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", "/login", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", "/login", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", "/login", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["line_token"] = rows[0]["linetoken"]

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
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", "/register", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", "/register", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", "/register", 400)

        # Ensure password matches confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", "/register", 400)

        username = request.form.get("username")

        rows = db.execute(
            "SELECT * FROM users WHERE username =?", (username,)
        ).fetchall()

        if len(rows) != 0:
            return apology("unavailable username", "/register", 400)

        hash = generate_password_hash(request.form.get("password"))

        # Insert user into database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username, hash))
        connection.commit()

        rows = db.execute(
            "SELECT * FROM users WHERE username =?", (username,)
        ).fetchall()
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/settoken", methods=["GET", "POST"])
def settoken():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("linetoken"):
            return apology("must provide token", "/settoken", 400)

        token = request.form.get("linetoken")
        userid = session["user_id"]

        message = '\nThank you for using iCRYPTO!\nSetting completed!'
        status = send_line_notify(message, token)
        if status == 200:
            db.execute(
                "UPDATE users SET linetoken =? WHERE id =?", (token, userid)
                )
            connection.commit()

            rows = db.execute(
                "SELECT * FROM users WHERE id =?", (userid,)
                ).fetchall()
            # Remember token is setted
            session["line_token"] = rows[0]["linetoken"]
        else:
            return apology("invalid token", "/settoken", 400)
        

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        userid = session["user_id"]
        row = db.execute(
            "SELECT linetoken FROM users WHERE id =?", (userid,)
        ).fetchall()
        if row[0]["linetoken"] == None:
            tokenstring = ""
        else:
            tokenstring = "value=" + row[0]["linetoken"]
        return render_template("settoken.html", tokenvalue=tokenstring)

@app.route("/setalert", methods=["GET", "POST"])
@login_required
def setalert():
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("missing symbol", "/setalert", 400)

        elif getprice(request.form.get("symbol")) == None:
            return apology("invalid symbol", "/setalert", 400)
        
        elif not request.form.get("change"):
            return apology("missing change", "/setalert", 400)

        elif not is_float(request.form.get("change")) or float(request.form.get("change")) < 0:
            return apology("invalid change", "/setalert", 400)

        symbol = request.form.get("symbol").upper()
        change = float(request.form.get("change"))
        userid = session["user_id"]
        price = getprice(symbol)
        # Check if symbol is setted
        asset = db.execute(
            "SELECT * FROM pricealert WHERE userid =? AND symbol =?", (userid, symbol)
            ).fetchall()

        if len(asset) != 1:
            db.execute(
                "INSERT INTO pricealert (userid, symbol, price, change) VALUES (?, ?, ?, ?)", (userid, symbol, price, change)
                )
            connection.commit()
        else:
            return apology("can't set same symbol", "/setalert", 400)

        # Redirect user to alertlist page
        return redirect("/alertlist")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("setalert.html")

@app.route("/stopalert", methods=["GET", "POST"])
@login_required
def stopalert():
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("missing symbol", "/stopalert", 400)

        symbol = request.form.get("symbol").upper()
        userid = session["user_id"]
        
        # Check if symbol is setted
        asset = db.execute(
            "SELECT * FROM pricealert WHERE userid =? AND symbol =?", (userid, symbol)
            ).fetchall()

        if len(asset) != 1:
            return apology("invalid symbol", "/stopalert", 400)
        else:
            db.execute(
                "DELETE FROM pricealert WHERE userid =? AND symbol =?", (userid, symbol)
                )
            connection.commit()

        # Redirect user to alertlist page
        return redirect("/alertlist")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        userid = session["user_id"]
        row = db.execute(
            "SELECT * FROM pricealert WHERE userid =?", (userid,)
        ).fetchall()
        return render_template("stopalert.html", rows=row)

@app.route("/alertlist")
@login_required
def alertlist():
    userid = session["user_id"]
    row = db.execute(
        "SELECT * FROM pricealert WHERE userid =?", (userid,)
    ).fetchall()
    return render_template("alertlist.html", rows=row)

if __name__ == '__main__':
    app.run(debug=True)