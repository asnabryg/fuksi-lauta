import re
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from os import getenv, urandom
from base64 import b64encode
from zlib import compress, decompress
from app import app

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = False
app.secret_key = urandom(16).hex()
db = SQLAlchemy(app)

import user

def savePicture(file, permission_id):

    # Tallentaa kuvan tietokantaan
    # Jos prosessi epäonnistuu, palautetaan tuple (False, error, error_message)
    # Jos onnisuu palautetaan (True, pic_id)
    # pic_id = juuri lisätyn kuvan id

    if not file.filename.endswith(".jpg"):
        return (False, "Kuvan lataus epäonnistui :(", "Virheellinen tiedostonimi")

    name = checkPicName(file.filename[:-4], session["user_id"]) # poistaa nimestä ".jpg" ja tarkastaa nimen
    data = file.read()
    print("orginal size:", len(data))
    data = compress(data)
    print("compress size:", len(data))
    if len(data) > 100 * 1024:
        return (False, "Kuvan lataus epäonnistui :(", "Tiedosto liian suuri, maximi koko 100 MB")
    
    try:
        sql = "INSERT INTO Pictures (name, data, permission, visible) VALUES (:name, :data, :permission, :visible) RETURNING id"
        pic_id = db.session.execute(sql, {"name": name, "data": data, "permission":permission_id, "visible":1}).fetchone()[0]
        db.session.commit()
    except:
        return (False, "Kuvan lataus epäonnistui :(", "Tuntematon virhe. Yritä myöhemmin uudellee.")

    return (True, pic_id)

def getPictureName(pic_id):
    sql = "SELECT name FROM Pictures WHERE id=:pic_id"
    return db.session.execute(sql, {"pic_id": pic_id}).fetchone()[0]

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
    if result is not None:
        if filename == result[0]:
            sql = "SELECT COUNT(*) FROM Pictures"
            count = db.session.execute(sql).fetchone()[0]
            filename += " (" + str(count + 1) + ")"
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
    return li


