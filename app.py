from os import name

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps

app = Flask(__name__)

app.secret_key = "dating-site-secret-key"

ADMIN_PASSWORD = "1234"
DATABASE = "database.db"


# =========================
# اتصال به دیتابیس
# =========================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =========================
# ساخت دیتابیس
# =========================

def create_database():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS dates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# =========================
# بررسی ورود ادمین
# =========================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, kwargs):

        if not session.get("admin"):
            return redirect(url_for("admin_login"))

        return function(*args, kwargs)

    return wrapper


# =========================
# صفحه اصلی
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# صفحه انتخاب قرار
# =========================

@app.route("/date", methods=["GET", "POST"])
def date_page():

    if request.method == "POST":

        location = request.form.get(
            "location",
            ""
        ).strip()

        date = request.form.get(
            "date",
            ""
        ).strip()

        time = request.form.get(
            "time",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()


        # بررسی کامل بودن اطلاعات

        if not location or not date or not time:

            return render_template(
                "date.html",
                error="لطفاً مکان، تاریخ و ساعت را کامل انتخاب کن."
            )


        # ذخیره اطلاعات

        connection = get_db()

        connection.execute(
            """
            INSERT INTO dates
            (location, date, time, message)
            VALUES (?, ?, ?, ?)
            """,
            (
                location,
                date,
                time,
                message
            )
        )

        connection.commit()
        connection.close()


        # رفتن به صفحه موفقیت

        return redirect(
            url_for("success")
        )


    return render_template(
        "date.html"
    )


# =========================
# صفحه موفقیت
# =========================

@app.route("/success")
def success():

    return render_template(
        "success.html"
    )


# =========================
# ورود ادمین
# =========================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin_login():

    # اگر قبلاً وارد شده
    if session.get("admin"):

        return redirect(
            url_for("admin_panel")
        )


    error = None


    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )


        if password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect(
                url_for("admin_panel")
            )


        error = "رمز عبور اشتباه است."


    return render_template(
        "admin_login.html",
        error=error
    )


# =========================
# پنل ادمین
# =========================

@app.route("/admin/panel")
@admin_required
def admin_panel():

    connection = get_db()


    dates = connection.execute(
        """
        SELECT *
        FROM dates
        ORDER BY id DESC
        """
    ).fetchall()


    connection.close()


    return render_template(
        "admin.html",
        dates=dates
    )


# =========================
# حذف یک قرار
# =========================
@app.route(
    "/admin/delete/<int:date_id>",
    methods=["POST"]
)
@admin_required
def delete_date(date_id):

    connection = get_db()


    connection.execute(
        """
        DELETE FROM dates
        WHERE id = ?
        """,
        (date_id,)
    )


    connection.commit()
    connection.close()


    return redirect(
        url_for("admin_panel")
    )


# =========================
# خروج ادمین
# =========================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================
# اجرای برنامه
# =========================

if __name__=="__main__":
    create_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )