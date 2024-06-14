from flask import redirect, render_template, session
from functools import wraps


def apology(message, backurl, code=400):
    """Render message as an apology to user."""

    return render_template("apology.html", top=code, bottom=message, back=backurl), code


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


def usd(value):
    """Format value as USD."""
    if value is None:
        return "---"
    return f"${value:,.4f}"

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False