from os import stat
import re
from flask.globals import session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db


def getUsername(user_id):
    sql = "SELECT username FROM Users WHERE id=:user_id"
    return db.session.execute(sql, {"user_id":user_id}).fetchone()[0]

def login(username, password, check=False):
    sql ="SELECT id, username, password FROM Users WHERE username=:username"
    user = db.session.execute(sql, {"username":username}).fetchone()
    if user == None:
        return False
    else:
        if check_password_hash(user[2], password):
            if not check:
                # Jos vain halutaan tarkastaa nimen ja salasanan oikeellisuus. Default = False
                session["user"] = user[1]
                session["user_id"] = user[0]
                updateOnlineStatus(username, 1)
            return True
        else:
            return False

def updateOnlineStatus(username, status: int):
    # päivittää käyttäjän online tilaa, 0: Offline, 1:Online
    sql = "UPDATE Users SET online=:s WHERE username=:username"
    db.session.execute(sql, {"s": status, "username": username})
    db.session.commit()

def getOnlineUsersCount():
    sql = "SELECT COUNT(*) FROM Users WHERE online=1"
    return db.session.execute(sql).fetchone()[0]

def getUserCount():
    sql = "SELECT COUNT(*) FROM Users"
    return db.session.execute(sql).fetchone()[0]

def is_admin():
    sql = "SELECT admin FROM Users WHERE username=:username"
    if "user" in session:
        result = db.session.execute(sql, {"username":session["user"]}).fetchone()[0]
        if result == 1:
            session["admin"] = True
            return True
    return False

def is_right_user(username):
    if "user" in session:
        return username == session["user"]
    return False

def update_password(username, new_password):
    hash_password = generate_password_hash(new_password)
    try:
        sql = "UPDATE Users SET password=:hash_password WHERE username=:username"
        db.session.execute(sql, {"hash_password":hash_password, "username":username})
        db.session.commit()
        # salasanan vaihto onnistui
        return True
    except:
        return False

def register(username, password1, password2):
    if not checkPassword(password1, password2):
        return (False, "Salasana ei täyttänyt suosituksia. Yritä uudelleen.")
    if not checkUsername(username):
        return (False, "Käyttäjä tunnus oli jo käytössä.")
    hash_pass = generate_password_hash(password1)
    try:
        sql = "INSERT INTO Users (username, password, admin, online) VALUES (:username, :password, :admin, :online)"
        db.session.execute(
            sql, {"username": username, "password": hash_pass, "admin": 0, "online": 0})
        db.session.commit()
    except:
        return (False, "Tuntematon virhe. Yritä myöhemmin uudelleen.")
    return (True, None)

def getProfilePic_id(username):
    # tarkistetaan ensin, onko pic_id
    sql = "SELECT pic_id FROM Users WHERE username=:username"
    result = db.session.execute(sql, {"username":username}).fetchone()
    if result[0] == None:
        #jos ei ole, etsitään default avatar kuvan id, ja pistetään se käyttjälle
        sql = "SELECT id FROM Pictures WHERE permission=0"
        default_img_id = db.session.execute(sql).fetchone()
        if default_img_id == None:
            #jos kuvia ei ole vielä lisätty tietokantaan
            return None
        sql = "UPDATE Users SET pic_id=:default_img_id WHERE username=:username"
        db.session.execute(sql, {"default_img_id":default_img_id[0], "username":username})
        db.session.commit()
        return 0
    return result[0]


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
    if not bool(re.search(r"[a-zA-Z]", pass1)):
        return False
    if len(pass1) < 8:
        return False
    return True
