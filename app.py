from flask import Flask
from flask import redirect, render_template, request
from flask.globals import session
from sqlalchemy.sql import elements
from sqlalchemy.sql.elements import Null
from werkzeug.security import check_password_hash, generate_password_hash
from zlib import compress

app = Flask(__name__)

import db as database
from db import db
import user
import topics as t
import messages as m

@app.route("/", methods=["GET", "POST"])
def index():
    check_info()
    topics_per_page = 10
    for x in session["topics_per_page"]:
        if x[1]:
            topics_per_page = x[0]
            break
    offset = (session["current_page"] * topics_per_page) - topics_per_page
    session["limit_offset"] = (topics_per_page, offset)
    topic_count = t.getTopicCount()
    if topic_count % topics_per_page == 0:
        page_count = topic_count // topics_per_page
    else:
        page_count = topic_count // topics_per_page + 1
    if request.method == "GET":
        sort_method = "vanhin_ensin"
        for s in session["sort"]:
            if s[1]:
                sort_method = s
                break
        print("SORT METHOD", sort_method)
        # (id, topic, info, user, time, pic_name, pic_data)
        topics = t.getLimitedAmountOfTopics(offset, topics_per_page, sort_method[0])
        for i in range(len(topics)):
            topic = list(topics[i])
            topic.append(topic.append(database.getProfilePictureData(topic[3])))
            topics[i] = topic
        print("topic_count:", t.getTopicCount())
        print("page_count:", page_count)
        print("topics_per_page", topics_per_page)
        print("offset:", offset)
        print("current_page:", session["current_page"])
        session["last_page"] = "/"
        return render_template("index.html", topics=topics, page_count=page_count, current=session["current_page"])
    else:
        if "page" in request.form:
            page = request.form["page"]
            if page == "seuraava":
                session["current_page"] = session["current_page"] + 1
            elif page == "edellinen":
                session["current_page"] = session["current_page"] - 1
            else:
                session["current_page"] = int(page)
        if "sort" in request.form:
            session["current_page"] = 1
            selectedSort = request.form["sort"]
            for i in range(len(session["sort"])):
                if session["sort"][i][0] == selectedSort:
                    session["sort"][i][1] = True
                else:
                    session["sort"][i][1] = False
        if "topics_per_page" in request.form:
            selectedAmount = request.form["topics_per_page"]
            for i in range(len(session["topics_per_page"])):
                if str(session["topics_per_page"][i][0]) == str(selectedAmount):
                    session["topics_per_page"][i][1] = True
                else:
                    session["topics_per_page"][i][1] =  False
        session["last_page"] = "/"
        return redirect("/")



@app.route("/login", methods=["GET", "POST"])
def login():
    print("LAST PAGE", session["last_page"])
    check_info()
    print("LAST PAGE", session["last_page"])
    user.is_admin() # tarkastaa onko admin
    if "user" in session:
        # jos käyttäjä jo kirjautunut sisään, ei tarvetta kirjautumis sivulle.
        if "/topic" in session["last_page"]:
            if "/topic" not in session["last_page"]:
                session["last_page"] = "/login"
            return redirect(session["last_page"])
        session["last_page"] = "/login"
        return redirect("/")
    if request.method == "GET":
        if "/topic" not in session["last_page"]:
            session["last_page"] = "/"
        return render_template("login.html", loginFail=False)
    else:
        username = request.form["username"]
        password = request.form["password"]
        if user.login(username, password):
            print("LAST PAGE", session["last_page"])
            if "topic" in session["last_page"]:
                print("ASDASDSADASDAS")
                last = session["last_page"]
                session["last_page"] = "/login"
                return redirect(last)
            print("EIEIEIE")
            session["last_page"] = "/login"
            return redirect("/")
        else:
            if "/topic" not in session["last_page"]:
                session["last_page"] = "/login"
            return render_template("login.html", loginFail=True)

@app.route("/logout")
def logout():
    check_info()
    user.updateOnlineStatus(session["user"], 0) #offline
    del session["user"]
    if user.is_admin():
        del session["admin"]
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    check_info()
    if "user" in session:
        # jos käyttäjä jo kirjautunut sisään, ei tarvetta rekistöytymis sivulle.
        session["last_page"] = "/register"
        return redirect("/")
    if request.method == "GET":
        if "/topic" not in session["last_page"]:
            session["last_page"] = "/register"
        return render_template("register.html", reg_succeed=False)
    else:
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        check = user.register(username, password1, password2)
        if check[0]:
            #rekistöröinti onnistui
            if "/topic" not in session["last_page"]:
                session["last_page"] = "/register"
            return render_template("register.html", reg_succeed=True, error_message=None)
        else:
            #ei onnistunut ja JS ei päällä, tai nimi oli jo käytössä, tai rekistöröintiä ei voitu tallentaa psql.
            if "/topic" not in session["last_page"]:
                session["last_page"] = "/register"
            return render_template("error.html", page="/register", error_type="Rekisteröinti ei onnistunut :(", error_message=check[1])



@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    allow = False
    check_info()
    if user.is_admin():
        allow = True
    if user.is_right_user(username):
        allow = True
    if not allow:
        # ei oikeutettu nähdä sivua!
        session["last_page"] = "/profile/" + username
        return render_template("error.html", page="/", error_type="Ei oikeuksia!", error_message="Et ole oikeutettu sivulle.")

    if request.method == "GET":
        # print("Picture:", user.getProfilePic_id(session["user"]))
        session["last_page"] = "/profile/" + username
        return render_template("profile.html", passUpdated=False, pic_data=database.getProfilePictureData(session["user"]), profile_pics=database.getProfilePicDict(session["user_id"]))
    else:
        #Jos vaihtaa salasanan
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        old_password = request.form["old_password"]
        check = user.checkPassword(password1, password2)
        if check:
            if user.login(session["user"], old_password, check=True):
                # jos vanha salasana täsmää -> vaihdetaan salasana
                if not user.update_password(session["user"], password1):
                    # tallentaa uuden salasanan if lausessa ja palauttaa booleanin, että onnistuiko
                    session["last_page"] = "/profile/" + username
                    return render_template(
                        "error.html", page="/profile/"+session['user'], error="Salasanan vaihto epäonnisui :(", error_message="Salasanan vahdossa ilmeni ongelmia. Yritä uudelleen.")
                else:
                    # vaihto onnisui
                    session["last_page"] = "/profile/" + username
                    return render_template("profile.html", passUpdated=True, pic_data=database.getProfilePictureData(session["user"]), profile_pics=database.getProfilePicDict(session["user_id"]))
            else:
                session["last_page"] = "/profile/" + username
                return render_template(
                    "error.html", page="/profile/"+session['user'], error="Salasanan vaihto epäonnisui :(", error_message="Vanha salasana oli väärin.")
        else:
            session["last_page"] = "/profile/" + username
            return render_template(
                "error.html", page="/profile/"+session['user'], error="Salasanan vaihto epäonnisui :(", error_message="Uusi salasana ei täyttänyt suosituksia")


@app.route("/savePicture", methods=["POST"])
def getProfilePicture():
    file = request.files["file"]
    permission_id = int(request.form["permission_id"])
    saved = database.savePicture(file, permission_id)
    if not saved[0]:
        # virhe tapahtui
        return render_template("error.html", page="/profile/"+session['user'], error=saved[1], error_message=saved[2])
    if permission_id > 0:
        # päivitetään Users tableen uusi profiilikuvan id
        # sql = "SELECT MAX(id) FROM Pictures WHERE permission=:permission_id"
        # pic_id = db.session.execute(sql, {"permission_id":permission_id}).fetchone()[0]
        pic_id = saved[1]
        sql = "UPDATE Users SET pic_id=:pic_id WHERE username=:username"
        db.session.execute(sql, {"pic_id":pic_id, "username":session["user"]})
        db.session.commit()
    return render_template("profile.html", passUpdated=False, pic_data=database.getProfilePictureData(session["user"]), profile_pics=database.getProfilePicDict(session["user_id"]))

@app.route("/changeProfilePic", methods=["POST"])
def changeProfilePic():
    pic_id = request.form["profile_pic"]
    sql = "UPDATE Users SET pic_id=:pic_id WHERE username=:username"
    db.session.execute(sql, {"pic_id": pic_id, "username": session["user"]})
    db.session.commit()
    return render_template("profile.html", passUpdated=False, pic_data=database.getProfilePictureData(session["user"]), profile_pics=database.getProfilePicDict(session["user_id"]))

@app.route("/topic<int:id>", methods=["GET", "POST"])
def topic(id):
    check_info()
    topic = list(t.getTopic(id)) # 0:topic_id, 1:user_id, 2:topic, 3:info, 4:time, 5:pic_id, 6:visits
    creator = user.getUsername(topic[1])
    topic.append(None) # nyt listan järjestys ei mee rikki, vaikka kuvaa ei olisi
    if topic[5] != None:
        pic_data = database.getPictureData(topic[5])
        pic_name = database.getPictureName(topic[5])
        topic[7] = pic_data
        topic[5] = pic_name
    topic[1] = creator
    topic.append(database.getProfilePictureData(creator))
    # Nyt topic on
    # [topic_id, username, topic, info, time, pic_name, pic_data, creator_profile_pic_data]
    if request.method == "POST":
        if "message" in request.form:
            # Viestin lähetys
            message = request.form["message"]
            file = request.files["file"]
            pic_id = None
            if file.filename != "":
                permission_id = request.form["permission_id"]
                saved = database.savePicture(file, permission_id)
                if not saved[0]:
                    # kuvan lähetys epäonnistui
                    session["last_page"] = "/topic" + str(id)
                    return render_template("topic.html", topic=topic, notSucceed=True, messages=m.getMessages(id))
                pic_id = saved[1]
            # lisätään viesti tietokantaan
            m.addMessageToTopic(message, pic_id, id, session["user_id"])
    messages = list(m.getMessages(id))
    # [[id, topic_id, username, content, pic_name, time, pic_data, profile_pic_data]]
    session["last_page"] = "/topic" + str(id)
    return render_template("topic.html", topic=topic, notSucceed=False, messages=messages)

@app.route("/newTopic", methods=["GET", "POST"])
def newTopic():
    check_info()
    if request.method == "GET":
        session["last_page"] = "/newTopic"
        return render_template("newTopic.html", notSucceed=False, topic="", info="")
    else:
        topic = request.form["topic"]
        info = request.form["info"]
        file = request.files["file"]
        pic_id = None
        print("lisääkö kuvan?")
        if file.filename != "":
            print("lisäsi kuvan")
            permission_id = request.form["permission_id"]
            saved = database.savePicture(file, permission_id)
            if not saved[0]:
                session["last_page"] = "/newTopic"
                return render_template("newTopic.html", notSucceed=True, topic=topic, info=info)
            pic_id = saved[1]
        # lisää topic tietokantaan
        sql = "INSERT INTO Topics (user_id, topic, info, time, pic_id) VALUES (:user_id, :topic, :info, NOW(), :pic_id)"
        db.session.execute(sql, {"user_id": int(session["user_id"]), "topic": topic, "info": info, "pic_id": pic_id})
        db.session.commit()
        session["last_page"] = "/newTopic"
        return redirect("/")

@app.route("/remove", methods=["POST"])
def remove():
    pass

def check_info():
    # Tämä metodi päivitetään, jokaisella eri sivun lataamis kerralla
    # Tarkistaa ip_osoitteen ja päivittää sen kävijöihin hashattuna, jos uusi kävijä
    # Tarkistaa milloin viimeksi käyty sivulla
    # Tarkstaa kuinka monta online käyttäjää sivustolla juuri nyt

    if "last_page" not in session:
        print("ASDSADSADSADSADSADSADASDSADSAJDÖKSAJDÖKJSADÖKSA")
        session["lsat_page"] = "/"
    if "topics_per_page" not in session:
        session["topics_per_page"] = [[5, False], [10, True], [15, False], [20, False], [25, False]]
    if "sort" not in session:
        session["sort"] = [["vanhin ensin", True], ["uusin ensin", False],
                           ["eniten viestejä", False]]
    if "limit_offset" not in session:
        session["limit_offset"] = (0, 10)
    if "current_page" not in session:
        session["current_page"] = 1
    headers_list = request.headers.getlist("X-Forwarded-For")
    user_ip = headers_list[0] if headers_list else request.remote_addr
    print("IP osoite:", user_ip)
    session["online_count"] = user.getOnlineUsersCount()
    if "visit_info" not in session:
        sql = "SELECT COUNT(*) from Visitors"
        visit_count = db.session.execute(sql).fetchone()[0]
        sql = "SELECT id, ip_address, last_visit from Visitors"
        ips = db.session.execute(sql).fetchall()
        for ip in ips:
            if check_password_hash(ip[1], user_ip):
                last_visit = ip[2]
                # päivittää viimeisimmän käynnin sivustolla tällä laitteella
                sql = "UPDATE Visitors SET last_visit=NOW() WHERE id=id"
                db.session.execute(sql, {"id": ip[0]})
                db.session.commit()
                if visit_count == 0:
                    session["visit_info"] = (1, None)
                    break
                else:
                    session["visit_info"] = (visit_count, last_visit)
                    break
        else:
            ip_address = generate_password_hash(
                user_ip, method='pbkdf2:sha256:1', salt_length=1)
            # lisää hashatun ip osoitteen tietokantaan
            sql = "INSERT INTO Visitors (ip_address, last_visit) VALUES (:ip_address, NOW())"
            db.session.execute(sql, {"ip_address": ip_address})
            db.session.commit()
            session["visit_info"] = (visit_count, None)
