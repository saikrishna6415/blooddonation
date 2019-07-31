from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

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
db = SQL("sqlite:///blooddonation.db")


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/home")
def home():

    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        if not request.form.get("username"):
            return "provide username"

        # Ensure bloodgroup was submitted
        elif not request.form.get("bloodgroup"):
            return "provide bloodgroup"

        elif not request.form.get("mobile"):
            return "must provide mobile"

        elif not request.form.get("address"):
            return "must provide address"

        elif not request.form.get("district"):
            return "must provide district"

        elif not request.form.get("password"):
            return "must provide password"

        elif not request.form.get("re-enter-password"):
            return "must provide re-enter-password"

        # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("re-enter-password"):
            return "passwords do not match"

        # hash the password and insert a new user in the database
        hashed = generate_password_hash(request.form.get("password"))
        donors = db.execute("INSERT INTO donors (username, bloodgroup, mobile, address, district, hash) VALUES(:username, :bloodgroup, :mobile, :address, :district, :hashed)",
                            username=request.form.get("username"), bloodgroup=request.form.get("bloodgroup"), mobile=request.form.get("mobile"), address=request.form.get("address"), district=request.form.get("district"),
                            hashed=hashed)

        # unique username constraint violated?
        if not donors:
            return "username taken"

            # Display a flash message
            flash("registered! Please login ") 

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
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
            return "must provide username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        # Query database for username
        rows = db.execute("SELECT * FROM donors WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "invalid username and/or password"

        # Remember which user has logged in
        session["user_name"] = rows[0]["username"]

        flash("Logged In")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/about")
def about():

    return render_template("about.html")


@app.route("/facts")
def facts():

    return render_template("facts.html")


@app.route("/find", methods=["GET", "POST"])
def find():

    if request.method == "POST":
        peoplefound = db.execute("SELECT * from donors WHERE bloodgroup = :bloodgroup AND district= :district",
                                 bloodgroup=request.form.get("bloodgroup"), district=request.form.get("district"))

        return render_template("found.html", peoplefound=peoplefound)
    else:
        return render_template("find.html")


@app.route("/requests", methods=["GET", "POST"])
def requests():
    if request.method == "POST":

        requestblood = db.execute("INSERT INTO bloodrequested (patientname, bloodgroup, mobile, address, district, hospital_name) VALUES(:patientname, :bloodgroup, :mobile, :address, :district, :hospital_name)",
                                  patientname=request.form.get("patientname"), bloodgroup=request.form.get("bloodgroup"), mobile=request.form.get("mobile"), address=request.form.get("address"), district=request.form.get("district"), hospital_name=request.form.get("hospital_name"))
        flash("blood requested")

        return redirect("/")
    else:
        return render_template("requests.html")


@app.route("/vission")
def vission():
    return render_template("vission.html")


@app.route("/whocan")
def whocan():

    return render_template("whocan.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))


@app.route("/bloodrequested", methods=["GET"])
def bloodrequested():
    if request.method == "GET":
        bloodrequested = db.execute("SELECT patientname, bloodgroup, mobile, address, district,hospital_name FROM bloodrequested")

    return render_template("bloodrequested.html", bloodrequested=bloodrequested)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
