import re
from flask.globals import session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db


def login(username, password):
    sql ="SELECT id, password FROM Users WHERE username=:username"
    user = db.session.execute(sql, {"username":username}).fetchone()
    if user == None:
        return False
    else:
        if check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return True
        else:
            return False

def register(username, password1, password2):
    if not checkPassword(password1, password2):
        return (False, "Salasana ei täyttänyt suosituksia. Yritä uudelleen.")
    if not checkUsername(username):
        return (False, "Käyttäjä tunnus oli jo käytössä.")
    hash_pass = generate_password_hash(password1)
    try:
        sql = "INSERT INTO Users (username, password, admin) VALUES (:username, :password, :admin)"
        db.session.execute(
            sql, {"username": username, "password": hash_pass, "admin": 0})
        db.session.commit()
    except:
        return (False, "Tuntematon virhe. Yritä myöhemmin uudelleen.")
    return (True, None)


def checkUsername(username):
    sql = "SELECT COUNT(username) FROM Users WHERE username=:username"
    exist = db.session.execute(sql, {"username": username}).fetchone()[0]
    if exist == 1:
        return False
    return True


def checkPassword(pass1, pass2):
    # tämä tarkastaa salasanan oikellisuuden, jos JavaScript on pois päältä
    if pass1 != pass2:
        return False
    if not bool(re.search(r"\d", pass1)):
        return False
    if len(pass1) < 8:
        return False
    return True
