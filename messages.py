from flask.globals import session
from flask.signals import message_flashed
from db import db
import db as database
import user


def addMessageToTopic(message, pic_id, topic_id, user_id):
    sql = "INSERT INTO Messages (content, pic_id, topic_id, time, user_id) VALUES (:message, :pic_id, :topic_id, NOW(), :user_id)"
    db.session.execute(sql, {"message": message,"pic_id": pic_id,"topic_id": topic_id, "user_id": user_id})
    db.session.commit()

def getMessages(topic_id, sort="vanhin ensin"):
    sql = ""
    if sort == "uusin ensin":
        sql = "SELECT M.*, SUM(CASE WHEN ML.vote=1 THEN 1 ELSE 0 END), SUM(CASE WHEN ML.vote=0 THEN 1 ELSE 0 END) FROM Messages M LEFT JOIN MessageLikes ML ON ML.message_id=M.id WHERE M.topic_id=:topic_id AND M.user_id >= 0 GROUP BY M.id ORDER BY M.id DESC"
    elif sort == "vanhin ensin":
        sql = "SELECT M.*, SUM(CASE WHEN ML.vote=1 THEN 1 ELSE 0 END), SUM(CASE WHEN ML.vote=0 THEN 1 ELSE 0 END) FROM Messages M LEFT JOIN MessageLikes ML ON ML.message_id=M.id WHERE M.topic_id=:topic_id AND M.user_id >= 0 GROUP BY M.id ORDER BY M.id"
    messages = db.session.execute(sql, {"topic_id": topic_id}).fetchall()
    if messages != []:
        user_votes = None
        if "user" in session:
            message_ids = ([m[0] for m in messages])
            sql = "SELECT message_id, vote FROM MessageLikes WHERE user_id=:user_id AND message_id= ANY(:message_ids)"
            user_votes = db.session.execute(sql, {"user_id": session["user_id"], "message_ids":message_ids}).fetchall()
        # [[id, topic_id, username, content, pic_name, time, pic_data, profile_pic_data]]
        for i in range(len(messages)):
            message = list(messages[i])
            message[2] = user.getUsername(
                message[2])  # vaihtaa user_id -> username
            if message[4] != None:
                pic_id = message[4]
                pic_name = database.getPictureName(
                    pic_id)
                pic_data = database.getPictureData(
                    pic_id)
                message[4] = (pic_name, pic_data)
            messages[i] = message
            vote = None
            if user_votes != None:
                for v in user_votes:
                    if v[0] == messages[i][0]:
                        vote = v[1]
            message.append(vote)
            message.append(database.getProfilePictureData(
                message[2]))  # lisää viestin lähettäjän profiilikuvan datan
    return messages

def removeMessage(message_id):
    try:
        sql = "DELETE FROM Messages WHERE id=:message_id"
        db.session.execute(sql, {"message_id": message_id, "user_id":session["user_id"]})
        db.session.commit()
        return True
    except:
        return False


def setVoteToMessage(message_id, user_id, vote):
    # tarkistetaan ensin onko jo tykätty
    sql = "SELECT vote FROM MessageLikes WHERE user_id=:user_id AND message_id=:message_id"
    result = db.session.execute(sql, {
        "user_id": user_id,
        "message_id": message_id
    }).fetchone()
    if result == None:
        sql = "INSERT INTO MessageLikes (message_id, user_id, vote) VALUES (:message_id, :user_id, :vote)"
    else:
        # jos result ja vote on samoja, poistetaan tykkäys
        if result[0] == 1 and vote == 1:
            vote = None
        if result[0] == 0 and vote == 0:
            vote = None
        sql = "UPDATE MessageLikes SET vote=:vote WHERE user_id=:user_id AND message_id=:message_id"
    db.session.execute(sql, {
        "message_id": message_id,
        "user_id": user_id,
        "vote": vote
    })
    db.session.commit()