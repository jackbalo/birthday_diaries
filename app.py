import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, calculate_age

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Homepage"""
    # Forget any user_id
    if "user_id" in session:
        return redirect("/home")
    else:
        session.clear()
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        phone = request.form.get("phone")
        dob = request.form.get("dob")
        name = request.form.get("name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        hash = generate_password_hash(password, method='pbkdf2:sha256:600000', salt_length=16)
            
        if not username or not password or not email or not phone or not name:
            return apology("All fields are required", 400)
        
        if password != confirmation:
            return apology("Password Mismatch", 400)
        
        try:
            db.execute("INSERT INTO users(name, username, hash, dob, email, phone) VALUES(?, ?, ?, ?, ?, ?)", name, username, hash, dob, email, phone)

            id_row= db.execute("SELECT * FROM users WHERE username= ?", username)
            user_id = id_row[0]["id"]
            db.execute("INSERT INTO audit_logs (user_id, action, timestamp) VALUES (?, ?, ?)", user_id, 'account_activatd', datetime.now())
            flash("Registration Succesful")
            return redirect("/login")
        
        except ValueError:
            return apology("Username already exists", 403)
    
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        #Add to logs
        log("log in")

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/home")
def home():
    '''Show friends whose birthday is that day'''
    if not session['user_id']:
        return render_template("layout.html")
    
    birthdays = db.execute("SELECT * FROM birthdays WHERE strftime('%d-%m', birthdates) = strftime('%d-%m', 'now') AND user_id = ?", session["user_id"])

    for friend in birthdays:
        birthdate = friend["birthdates"]
        friend["age"] = calculate_age(birthdate)

    return render_template("home.html", birthdays=birthdays)


@app.route("/birthdays")
@login_required
def birthdays():
    '''list all friends and their birthdays'''
    birthdays = db.execute("SELECT * FROM birthdays WHERE user_id = ?", session["user_id"])

    for friend in birthdays:
        birthdate = friend["birthdates"]
        friend["age"] = calculate_age(birthdate)

    return render_template("birthdays.html", birthdays=birthdays)


@app.route("/add_birthday", methods=["GET", "POST"])
@login_required
def add_birthday():
    '''add Friend's birthday'''
    if request.method == "POST":
        email = request.form.get("email")
        phone = request.form.get("phone")
        birthdate = request.form.get("birthdate")
        name = request.form.get("name")

        if not name or not birthdate or not phone or not email:
            flash("All fields are required")
    
        db.execute("INSERT INTO birthdays(user_id, name, birthdates, phone, email) VALUES(?, ?, ?, ?, ?)", session['user_id'], name, birthdate, phone, email)

        log(f"added_{name}")
        flash(f"{name} added successfully")
        return redirect("/birthdays")
    else:
        return render_template("add.html")


@app.route("/delete_birthday/<int:id>", methods=["GET", "POST"])
@login_required
def delete_friend(id):
    '''Delete or Change Friend's birthday'''
    row = db.execute("SELECT * FROM birthdays WHERE id = ? AND user_id = ?", id, session['user_id'])
    name = row[0]["name"]

    db.execute("DELETE FROM birthdays WHERE id = ? AND user_id = ?", id, session['user_id'])

    log(f"deleted_{name}")
    flash(f"{name} deleted from friends")
    return redirect("/birthdays")


@app.route("/edit_birthday/<int:id>", methods=["GET", "POST"])
@login_required
def edit_birthday(id):
    '''Change Friend's birthday'''
    friend_row = db.execute("SELECT * FROM birthdays WHERE id = ? AND user_id = ?", id, session['user_id'])
    if not friend_row:
        flash("not in Friend's list")
        return redirect("/birthdays")
    
    friend = friend_row[0] #turn list of dictionaries into a single dictionary.
    if request.method == "POST":
        email = request.form.get("email") or friend["email"]
        phone = request.form.get("phone") or friend["phone"]
        birthdate = request.form.get("birthdate") or friend["birthdates"]
        name = request.form.get("name") or friend["name"]
    
        db.execute("UPDATE birthdays SET name = ?, birthdates = ?, phone = ?, email = ?", name, birthdate, phone, email)

        log(f"edited_{name}")
        flash("Successful")
        return redirect("/birthdays")
    
    else:
        return render_template("edit.html", friend=friend)


@app.route("/update_profile/<int:id>", methods=["GET", "POST"])
@login_required
def update_profile(id):
    '''Change Friend's birthday'''
    user_row = db.execute("SELECT * FROM users WHERE id = ?", id)
    if not user_row:
        flash("Invalid action")
        return redirect("/birthdays")
    
    user = user_row[0] #turn list of dictionaries into a single dictionary.
    if request.method == "POST":
        name = request.form.get("name") or user["name"]
        username = request.form.get("username") or user["username"]
        email = request.form.get("email") or user["email"]
        phone = request.form.get("phone") or user["phone"]
        dob =  request.form.get("dob") or user["dob"]
        password = request.form.get("password")

        if not password or not check_password_hash(user["hash"], password):
            flash("Enter Valid password")
            return redirect("/update_profile/<int:id>")

        db.execute("UPDATE users SET name = ?, username = ?, phone = ?, email = ?, dob = ? WHERE id = ?", name, username, phone, email, dob, id)

        log("profile_update")
        flash("Profile updated succefully")
        return redirect("/profile")
    
    else:
        return render_template("update_profile.html", user=user)
    

@app.route("/logout")
def logout():
    """Log user out"""
    user_id = session["user_id"]
    
    #Add to logs
    log("log out")

    # Forget any user_id
    session.clear()
    

    # Redirect user to login form
    return redirect("/")


@app.route("/password_reset", methods=["GET", "POST"])
@login_required
def password_reset():
    """Change User Password"""
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        hash = generate_password_hash(new_password, method='pbkdf2:sha256:600000', salt_length=16)
        
        if not old_password:
            flash("Enter Current Password")
            return redirect("/password_reset") 
        
        if not new_password or new_password != confirmation:
            flash("Password Mismatch")
            return redirect("/password_reset")
        
        db.execute("UPDATE users SET hash = ?", hash)
        
        log("pword_reset")
        flash("Password Changed Successfully")
        return redirect("/")

    else:
        return render_template("password_reset.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search for friend"""
    if request.method == "POST":
        name = request.form.get("name")
        
        if not name:
            flash("Enter a valid friend's name")
            return redirect("/index")
        
        searched_name = f"%{name}%"
        
        birthdays = db.execute("SELECT * FROM birthdays WHERE name LIKE ? AND user_id = ?", searched_name, session['user_id'])

        for friend in birthdays:
            birthdate = friend["birthdates"]
            friend["age"] = calculate_age(birthdate)

        return render_template("birthdays.html", birthdays=birthdays)

    else:
        return redirect("/home")
    

@app.route("/profile")
@login_required
def profile():
    '''view Your Account'''
    user_row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    user = user_row[0]

    return render_template("profile.html", user=user)


@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    '''Delete Your Account'''
    if request.method == "POST":
        password = request.form.get("password")
        user_id = session["user_id"]
        if not user_id:
            flash("Log in to perform this action")
            return redirect("/login")
        
        row = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        hash = row[0]["hash"]
        
        if not password or not check_password_hash(hash, password):
            flash("Enter a valid password")
            return redirect("/profile")
        
        db.execute("DELETE FROM users WHERE id =?", user_id)
        
        db.execute("DELETE FROM birthdays WHERE user_id = ?", user_id)
        
        log('account_deleted')
        session.clear()
        flash("Your account has been deactivated")
        
        return redirect("/register")



def log(action):
    user_id = session["user_id"]
            
    return db.execute("INSERT INTO audit_logs (user_id, action, timestamp) VALUES (?, ?, ?)", user_id, action, datetime.now())