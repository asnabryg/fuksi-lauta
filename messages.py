from db import db
import db as database
import user


def addMessageToTopic(message, pic_id, topic_id, user_id):
    sql = "INSERT INTO Messages (content, pic_id, topic_id, time, user_id) VALUES (:message, :pic_id, :topic_id, NOW(), :user_id)"
    db.session.execute(sql, {"message": message,"pic_id": pic_id,"topic_id": topic_id, "user_id": user_id})
    db.session.commit()

def getMessages(topic_id, sort="uusin ensin"):
    sql = ""
    if sort == "uusin ensin":
        sql = "SELECT * FROM Messages WHERE topic_id=:topic_id AND user_id >= 0 ORDER BY id DESC"
    elif sort == "vanhin ensin":
        sql = "SELECT * FROM Messages WHERE topic_id=:topic_id AND user_id >= 0 ORDER BY id"
    messages = db.session.execute(sql, {"topic_id": topic_id}).fetchall()
    if messages != []:
        print("MESSAGE", messages)

        for i in range(len(messages)):
            message = list(messages[i])
            message[2] = user.getUsername(
                message[2])  # vaihtaa user_id -> username
            message.append(None)  # lista ei mee rikki
            if message[4] != None:
                pic_id = message[4]
                message[4] = database.getPictureName(
                    pic_id)  # vaihtaa pic_id -> pic_name
                message[6] = database.getPictureData(
                    pic_id)  # lisää viestissä lähetetyn kuvan datan
            message.append(database.getProfilePictureData(
                message[2]))  # lisää viestin lähettäjän profiilikuvan datan
            messages[i] = message
    return messages