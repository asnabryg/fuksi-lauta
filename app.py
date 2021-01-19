from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route("/")
def index():
    # palauttaa ajan milloin viimeksi kävit tällä laitteella sivustolla
    visit_info = check_ip()
    return render_template("index.html", visit_info=visit_info)


def check_ip():
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
                return 1, None
            else:
                return visit_count, last_visit
    # else
    ip_address = generate_password_hash(
        request.remote_addr, method='pbkdf2:sha256:1', salt_length=1)
    # lisää hashatun ip osoitteen tietokantaan
    sql = "INSERT INTO Visitors (ip_address, last_visit) VALUES (:ip_address, NOW())"
    db.session.execute(sql, {"ip_address": ip_address})
    db.session.commit()
    return visit_count, None
