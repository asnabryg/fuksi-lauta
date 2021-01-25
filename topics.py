import re
from flask.globals import session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
import db as database
import user


def getTopicCount():
    sql = "SELECT COUNT(*) FROM Topics"
    return db.session.execute(sql).fetchone()[0]

def getTopic(topic_id):
    sql = "SELECT * FROM Topics WHERE id=:topic_id"
    return db.session.execute(sql, {"topic_id": topic_id}).fetchone()

def getTopicsByMostMessages(topic_amount = 10):
    sql = "SELECT topic_id FROM Messages GROUP BY topic_id ORDER BY COUNT(id) LIMIT 10"
    return db.session.execute(sql).fetchall()

def getLimitedAmountOfTopics(mista=0, mihin=10, order="vanhin ensin"):
    # orders: "oldest", "newest", "most_messages", "most_visits", "last_messages"
    results = None
    if order == "eniten viestejä":
        sql = "SELECT topic_id FROM Messages GROUP BY topic_id ORDER BY COUNT(id) LIMIT :mihin OFFSET :mista"
        results = db.session.execute(sql, {"mihin": mihin, "mista": mista}).fetchall()
        if results == []:
            order = "oldest"

    if order == "vanhin ensin":
        sql = "SELECT * FROM Topics LIMIT :mihin OFFSET :mista"
        results = db.session.execute(sql, {"mihin": mihin, "mista": mista}).fetchall()

    if order == "uusin ensin":
        sql = "SELECT * FROM Topics ORDER BY id DESC LIMIT :mihin OFFSET :mista"
        results = db.session.execute(sql, {"mihin": mihin, "mista":mista}).fetchall()

    if results is None:
        return None
    li = []
    # 10 limit per sivu
    if results != []:
        for i in range(len(results)):
            # (id, topic, info, user, time, pic_name, pic_data)
            pic_name = None
            pic_data = None
            if results[i][5] != None:
                pic_name = database.getPictureName(results[i][5])
                pic_data = database.getPictureData(results[i][5])
            li.append((results[i][0], results[i][2], results[i][3], user.getUsername(results[i][1]), results[i][4], pic_name, pic_data))
    return li

def removeTopic(topic_id):
    try:
        sql = "DELETE FROM Topics WHERE id=:topic_id"
        db.session.execute(sql, {"topic_id":topic_id})
        db.session.commit()
        return True
    except:
        return False