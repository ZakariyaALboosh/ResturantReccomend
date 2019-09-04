import os
import urllib.parse
from cs50 import SQL
from flask import Flask, flash, jsonify, json, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///FP.db")

#homepage route
@app.route("/")
@login_required
def index():
    return render_template("index.html")




@app.route("/submit-review", methods=["POST"])
@login_required
def submitReview():
    #enters review into database table posts
    if request.method == "POST":
        shopname = request.form.get("shopname")
        username = session['username']
        outoften = request.form.get("outoften")
        review = request.form.get("review")
        result = db.execute("INSERT into posts(shopname, username, outoften, review) VALUES(:shopname, :username, :outoften, :review) ",
        shopname = shopname,
        username = username,
        outoften = outoften,
        review = review
        )
    posts = db.execute("SELECT * FROM posts WHERE shopname = :shopname", shopname = shopname)
    return redirect("/place/" + shopname)



#route for each resturant
@app.route("/place/<string:shopname>", methods=["GET"])
@login_required
def shop(shopname):
    shopname = urllib.parse.unquote(shopname)
    print("HERE HERE   " + shopname)
    #shows reviews and renders template for submitting
    placeinfo = db.execute("SELECT * FROM placeinfo WHERE shopname = :shopname", shopname = shopname)
    posts = db.execute("SELECT * FROM posts WHERE shopname = :shopname", shopname = shopname)
    image = shopname + ".jpg"
    place = shopname
    return render_template("shop.html", posts = posts, image = image, place = place, placeinfo = placeinfo)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
#self explanatory
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return 403

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("wrong user or pass ", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

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
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        if not username or not password or not confirm:
            return apology("All fields required")
        if password != confirm:
            return apology("password doesn't match")
        passhash = generate_password_hash(password)
        check = db.execute("SELECT username from users WHERE username = :userin", userin = username)
        if not check:
            result = db.execute("INSERT INTO users(username,hash) VALUES(:username, :phash)", username= username , phash = passhash)
            if not result:
                return apology("database error")
            new = db.execute("SELECT * FROM users WHERE username = :username", username=username)
            session["user_id"] = new[0]["id"]
            session["username"] = new[0]["username"]

            return redirect("/")
        else:
            return apology("username taken", 400)
    return render_template("register.html")





#error handler by cs50
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


@app.route("/check", methods=["GET"])
def check():
    result = db.execute("SELECT username from users WHERE username = :userin", userin = request.args.get("username"))
    if  len(result) == 0 :
        return jsonify(True)
    else:
        return jsonify(False)


#Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
