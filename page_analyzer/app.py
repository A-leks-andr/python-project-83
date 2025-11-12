import os
import psycopg2
from contextlib import contextmanager


from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    get_flashed_messages,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.url_utils import normalize_url, validate_url
from page_analyzer.db import Url_Repository, get_db

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")


@contextmanager
def get_repo():
    conn = get_db(app)
    repo = Url_Repository(conn)
    try:
        yield repo
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        repo.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls", methods=["POST"])
def urls_post():
    url_data = request.form.to_dict()
    url_name = url_data.get("url")

    if not url_name:
        flash("URL не может быть пустым", "error")
        return redirect(url_for("index"))

    errors = validate_url(url_name)
    if errors:
        return render_template("index.html", url=url_name, errors=errors), 422

    url_normalized = normalize_url(url_name)
    with get_repo() as repo:
        url = repo.get_url_by_name(url_normalized)
        if not url:
            url = repo.create_url(url_normalized)
            flash("Страница успешно добавлена", "success")
        else:
            flash("Страница уже существует", "info")
        return redirect(url_for("urls_show", id=url.id))


@app.route("/urls/<int:id>")
def urls_show(id):
    with get_repo() as repo:
        url = repo.get_url_by_id(id)
        if not url:
            abort(404)
        url_check = repo.get_checks_for_urls(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "show.html", url=url, checks=url_check, messages=messages
    )
