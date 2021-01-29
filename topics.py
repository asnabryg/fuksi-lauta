import re
from flask import app
from flask.globals import session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
import db as database
import user


def addNewTopic(user_id, topic, info, pic_id, theme):
    try:
        sql = "INSERT INTO Topics (user_id, topic, info, pic_id, theme, time) VALUES (:user_id, :topic, :info, :pic_id, :theme, NOW())"
        db.session.execute(sql, {"user_id": user_id, "topic": topic, "info": info, "pic_id": pic_id, "theme": theme})
        db.session.commit()
        return True
    except:
        return False


def getTopicCount(theme="Kaikki", search=""):
    parts = search.split(" ")
    search = "|".join(parts)
    search = "%(" + search + ")%"
    if theme == "Kaikki":
        theme = None
    sql = "SELECT COUNT(*) FROM Topics WHERE theme=(CASE WHEN :theme IS NOT NULL THEN :theme ELSE theme END) AND (LOWER(topic) SIMILAR TO :search OR LOWER(info) SIMILAR TO :search)"
    return db.session.execute(sql, {"theme": theme, "search": search}).fetchone()[0]

def getTopic(topic_id):
    sql = "SELECT * FROM Topics WHERE id=:topic_id"
    return db.session.execute(sql, {"topic_id": topic_id}).fetchone()

def getTopicsByMostMessages(topic_amount = 10):
    sql = "SELECT topic_id FROM Messages GROUP BY topic_id ORDER BY COUNT(id) LIMIT 10"
    return db.session.execute(sql).fetchall()

def getLimitedAmountOfTopics(mista=0, mihin=10, order="", theme="Kaikki", search=""):
    # orders: "oldest", "newest", "most_messages", "most_visits", "last_messages"
    parts = search.split(" ")
    search = "|".join(parts)
    search = "%(" + search + ")%"
    results = None
    if theme == "Kaikki":
        theme = None

    if order == "eniten viestejä":
        # topic = (id, user_id, topic, info, time, pic_id, visits, theme)
        sql = "SELECT T.*, SUM(CASE WHEN TL.vote=1 THEN 1 ELSE 0 END), SUM(CASE WHEN TL.vote=0 THEN 1 ELSE 0 END) FROM Topics T LEFT JOIN Messages M ON M.topic_id=T.id LEFT JOIN TopicLikes TL ON T.id=TL.topic_id AND T.theme=(CASE WHEN :theme IS NOT NULL THEN :theme ELSE T.theme END) AND (LOWER(T.topic) SIMILAR TO :search OR LOWER(T.info) SIMILAR TO :search) GROUP BY T.id ORDER BY COUNT(M.*) DESC LIMIT :mihin OFFSET :mista"
        results = db.session.execute(sql, {"mihin": mihin, "mista": mista, "theme": theme, "search": search}).fetchall()
        if results == []:
            order = "vanhin ensin"

    if order == "vanhin ensin":
        sql = "SELECT T.*, sum(case when TL.vote=1 then 1 else 0 end), sum(case when TL.vote=0 then 1 else 0 end) FROM Topics T LEFT JOIN TopicLikes TL ON T.id=TL.topic_id AND T.theme=(CASE WHEN :theme IS NOT NULL THEN :theme ELSE T.theme END) AND (LOWER(T.topic) SIMILAR TO :search OR LOWER(T.info) SIMILAR TO :search) GROUP BY T.id LIMIT :mihin OFFSET :mista"
        results = db.session.execute(sql, {"mihin": mihin, "mista": mista, "theme": theme, "search": search}).fetchall()
    if order == "uusin ensin":
        sql = "SELECT T.*, sum(case when TL.vote=1 then 1 else 0 end), sum(case when TL.vote=0 then 1 else 0 end) FROM Topics T LEFT JOIN TopicLikes TL ON T.id=TL.topic_id AND T.theme=(CASE WHEN :theme IS NOT NULL THEN :theme ELSE T.theme END) AND (LOWER(T.topic) SIMILAR TO :search OR LOWER(T.info) SIMILAR TO :search) GROUP BY T.id ORDER BY T.id desc LIMIT :mihin OFFSET :mista"
        results = db.session.execute(sql, {"mihin": mihin, "mista":mista, "theme":theme, "search": search}).fetchall()

    if results is None:
        return None
    palautus = []
    # 10 limit per sivu
    # (id, topic, info, user, time, pic_name, pic_data, upvotes, downvotes)
    if results != []:
        user_votes = None
        if "user" in session:
            topic_ids = ([t[0] for t in results])
            sql = "SELECT topic_id, vote FROM TopicLikes WHERE user_id=:user_id AND topic_id= ANY(:topic_ids)"
            user_votes = db.session.execute(sql, {"user_id": session["user_id"], "topic_ids": topic_ids}).fetchall()
        for i in range(len(results)):
            pic_name = None
            pic_data = None
            username = user.getUsername(results[i][1])
            if results[i][5] != None: # Jos topicissa on kuva, haetaan kuvan nimi ja data
                pic_name = database.getPictureName(results[i][5])
                pic_data = database.getPictureData(results[i][5])
            profile_pic_data = database.getProfilePictureData(username)
            message_count = getMessageCount(results[i][0])
            vote = None
            if user_votes != None:
                for v in user_votes: # haetaan käyttäjän tykkäys, None jos ei ole kirjautunut tai ei ole tykännyt aiheesta
                    if v[0] == results[i][0]:
                        vote = v[1]
            palautus.append([results[i][0], results[i][2], results[i][3],
                             username, results[i][4],
                             pic_name, pic_data, profile_pic_data, results[i][8], results[i][9], message_count, vote])
    # (id, topic, info, user, time, pic_name, pic_data, profile_pic_data, upvotes, downvotes, message_count, vote)
    return palautus


def removeTopic(topic_id):
    try:
        sql = "DELETE FROM Topics WHERE id=:topic_id"
        db.session.execute(sql, {"topic_id":topic_id})
        db.session.commit()
        return True
    except:
        return False

def getMessageCount(topic_id):
    sql = "SELECT COUNT(*) FROM Messages WHERE topic_id=:topic_id"
    return db.session.execute(sql, {"topic_id":topic_id}).fetchone()[0]

def getUserTopivVote(user_id):
    sql = ""

def setVoteToTopic(topic_id, user_id, vote, topic_index = None):
    # tarkistetaan ensin onko jo tykätty
    sql = "SELECT vote FROM TopicLikes WHERE user_id=:user_id AND topic_id=:topic_id"
    result = db.session.execute(sql, {"user_id": user_id, "topic_id": topic_id}).fetchone()
    index_and_vote = None
    if result == None:
        if vote == 1:
            index_and_vote = [8, 1]
        if vote == 0:
            index_and_vote = [9, 1]
        sql = "INSERT INTO TopicLikes (topic_id, user_id, vote) VALUES (:topic_id, :user_id, :vote)"
    else:
        # jos result ja vote on samoja, poistetaan tykkäys
        if result[0] == 1 and vote == 1:
            index_and_vote = [8, -1]
            vote = None
        elif vote == 1:
            index_and_vote = [8, 1]
        if result[0] == 0 and vote == 0:
            index_and_vote = [9, -1]
            vote = None
        elif vote == 0:
            index_and_vote = [9, 1]
        sql = "UPDATE TopicLikes SET vote=:vote WHERE user_id=:user_id AND topic_id=:topic_id"
    index_and_vote.append(vote)  # vote_index, change value, vote=None/1/0
    db.session.execute(sql, {"topic_id": topic_id, "user_id": user_id, "vote": vote})
    db.session.commit()
    return index_and_vote # palauttaa vote_indexin ja +- arvon, jolla voidaan poistaa/lisaa vote muistissaolleessa topicciin
