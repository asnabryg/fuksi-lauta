from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from os import getenv, urandom
from base64 import b64encode
from zlib import decompress
from app import app

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = urandom(16).hex()
db = SQLAlchemy(app)

import user

def getPictureData(pic_id):
    sql = "SELECT data FROM Pictures WHERE id=:pic_id"
    data = db.session.execute(sql, {"pic_id":pic_id}).fetchone()[0]
    return b64encode(decompress(data)).decode("utf-8")


def getProfilePictureData(username):
    pic_id = user.getProfilePic_id(username)
    sql = "SELECT data FROM Pictures WHERE id=:pic_id"
    data = db.session.execute(sql, {"pic_id": pic_id}).fetchone()
    if data is not None:
        return b64encode(decompress(data[0])).decode("utf-8")
    else:
        return None

def checkPicName(filename, user_id):
    # tarkastaa jos jo saman niminen kuva lisätty omiin profilikuviin
    # jos on niin lisää (uuden id) perään
    sql = "SELECT name FROM Pictures WHERE name=:filename AND permission=:user_id"
    result = db.session.execute(sql, {"filename":filename, "user_id":user_id}).fetchone()
    print("RESULTS", result)
    if result is not None:
        if filename == result[0]:
            sql = "SELECT COUNT(*) FROM Pictures"
            count = db.session.execute(sql).fetchone()[0]
            filename += " (" + str(count + 1) + ")"
            print("UUSI NIMI:", filename)
    return filename

def getProfilePicDict(user_id):
    # hakee kaikki käyttäjänprofiilikuvat, joita ei ole poistettu
    # ja lisää ne listaan tuplena (pic_id, pic_name)
    # ensimmäinen kuva on käytössä oleva profiilikuva
    li = []
    sql = "SELECT pic_id FROM Users WHERE id=:user_id"
    in_Use_id = db.session.execute(sql, {"user_id":user_id}).fetchone()[0]
    sql = "SELECT id, name FROM Pictures WHERE permission=:user_id OR permission=0"
    results = db.session.execute(sql, {"user_id":user_id}).fetchall()
    for result in results:
        if result[0] == in_Use_id:
            li.insert(0, (result[0], result[1]))
        else:
            li.append((result[0], result[1]))
    print("KUVAT:", li)
    return li

