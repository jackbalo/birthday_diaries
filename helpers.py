import requests
import random

from datetime import datetime, timedelta
from flask import redirect, render_template, session

from twilio.rest import Client
from email.mime.text import MIMEText
import smtplib

from functools import wraps


# Temporary OTP storage (use Redis or DB in production)
otps = {}

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

#to lookup a friend
def lookup(friend):
    """Look up quote for symbol."""
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}" #change this url
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper()
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None

# calculate the age of a friend
def calculate_age(birthdate) ->int: #Take an input birthdate and then output(->) an integer

    #check to see if date format is a date or datetime and if not formats in year-month-day
    if isinstance(birthdate, str): #
        birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
    
    today = datetime.today()
    age = today.year - birthdate.year

    # check if the friend has already celebrated his birthday for the year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1

    return age


def generate_otp(user_id):
    """Generate a random 6-digit OTP"""
    otp = random.randint(100000, 999999)
    otps[user_id] = {"otp": otp, "expires_at": datetime.now() + timedelta(minutes=5)}
    return otp

def verify_otp(user_id, entered_otp):
    """Verify OTP"""
    if user_id in otps:
        otp_data = otps[user_id]
        if otp_data["otp"] == int(entered_otp) and otp_data["expires_at"] > datetime.now():
            del otps[user_id]  # Remove OTP after verification
            return True
    return False

def send_sms(phone_number, otp):
    """Send OTP via SMS"""
    account_sid = "your_twilio_account_sid"
    auth_token = "your_twilio_auth_token"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your verification code is: {otp}",
        from_="+1234567890",  # Your Twilio number
        to=phone_number
    )
    return message.sid

def send_email(recipient_email, otp):
    """Send OTP via Email"""
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"

    subject = "Verification Code"
    body = f"Your OTP code is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

