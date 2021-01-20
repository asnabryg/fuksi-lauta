from flask import Flask
from flask import redirect, render_template, request
from flask.globals import session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

from db import db
import user


@app.route("/")
def index():
    # palauttaa ajan milloin viimeksi kävit tällä laitteella sivustolla
    check_info()
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    check_info()
    if "user" in session:
        # jos käyttäjä jo kirjautunut sisään, ei tarvetta kirjautumis sivulle.
        return redirect("/")
    if request.method == "GET":
        return render_template("login.html", loginFail=False)
    else:
        username = request.form["username"]
        password = request.form["password"]
        if user.login(username, password):
            return redirect("/")
        else:
            return render_template("login.html", loginFail=True)
            
@app.route("/logout")
def logout():
    check_info()
    user.updateOnlineStatus(session["user"], 0) #offline
    del session["user"]
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    check_info()
    if "user" in session:
        # jos käyttäjä jo kirjautunut sisään, ei tarvetta rekistöytymis sivulle.
        return redirect("/")
    if request.method == "GET":
        return render_template("register.html", reg_succeed=False)
    else:
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        check = user.register(username, password1, password2)
        print("CHECK:", check)
        if check[0]:
            #rekistöröinti onnistui
            return render_template("register.html", reg_succeed=True, error_message=None)
        else:
            #ei onnistunut ja JS ei päällä, tai nimi oli jo käytössä, tai rekistöröintiä ei voitu tallentaa psql.
            return render_template("error.html", page="/register", error_type="Rekisteröinti ei onnistunut :(", error_message=check[1])



@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    check_info()
    if request.method == "GET":
        return render_template("profile.html", passUpdated=False)
    else:
        #Jos vaihtaa salasanan
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        old_password = request.form["old_password"]
        check = user.checkPassword(password1, password2)
        print("check:", check)
        if check:
            if user.login(session["user"], old_password, check=True):
                # jos vanha salasana täsmää -> vaihdetaan salasana
                if not user.update_password(session["user"], password1):
                    # tallentaa uuden salasanan if lausessa ja palauttaa booleanin, että onnistuiko
                    return render_template(
                        "error.html", page="/profile/{{session['user']}}", error="Salasanan vaihto epäonnisui :(", error_message="Salasanan vahdossa ilmeni ongelmia. Yritä uudelleen.")
                else:
                    # vaihto onnisui
                    return render_template("profile.html", passUpdated=True)
            else:
                return render_template(
                    "error.html", page="/profile/{{session['user']}}", error="Salasanan vaihto epäonnisui :(", error_message="Vanha salasana oli väärin.")
        else:
            return render_template(
                "error.html", page="/profile/{{session['user']}}", error="Salasanan vaihto epäonnisui :(", error_message="Uusi salasana ei täyttänyt suosituksia")

def check_info():
    # Tämä metodi päivitetään, jokaisella eri sivun lataamis kerralla
    # Tarkistaa ip_osoitteen ja päivittää sen kävijöihin hashattuna, jos uusi kävijä
    # Tarkistaa milloin viimeksi käyty sivulla
    # Tarkstaa kuinka monta online käyttäjää sivustolla juuri nyt

    session["online_count"] = user.getOnlineUsersCount()
    
    if "visit_info" not in session:
        sql = "SELECT COUNT(*) from Visitors"
        visit_count = db.session.execute(sql).fetchone()[0]
        sql = "SELECT id, ip_address, last_visit from Visitors"
        ips = db.session.execute(sql).fetchall()
        for ip in ips:
            if check_password_hash(ip[1], request.remote_addr):
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
                request.remote_addr, method='pbkdf2:sha256:1', salt_length=1)
            # lisää hashatun ip osoitteen tietokantaan
            sql = "INSERT INTO Visitors (ip_address, last_visit) VALUES (:ip_address, NOW())"
            db.session.execute(sql, {"ip_address": ip_address})
            db.session.commit()
            session["visit_info"] = (visit_count, None)
