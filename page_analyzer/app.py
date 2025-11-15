import os
from contextlib import contextmanager

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.date import URL, URLCheck
from page_analyzer.db import Url_Repository, get_db
from page_analyzer.parser_handler import (
    ErrorResponse,
    get,
    get_seo_content,
)
from page_analyzer.url_utils import normalize_url, validate_url

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
            if not url:
                flash("Не удалось добавить страницу", "error")
                return redirect(url_for("index"))
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
        url_check = repo.get_checks_for_url(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "show.html", url=url, checks=url_check, messages=messages
    )


@app.route("/urls/<int:id>/checks", methods=["POST"])
def checks_post(id):
    with get_repo() as repo:
        url = repo.get_url_by_id(id)
        if not url:
            abort(404)

        resp = get(url.name, app.logger)

        if resp is None:
            flash("Не удалось получить ответ от сервера", "error")
            return redirect(url_for("urls_show", id=id))

        elif isinstance(resp, ErrorResponse):
            flash(resp.error, "error")
            return redirect(url_for("urls_show", id=id))

        h1, title, description = get_seo_content(resp.content, app.logger)

        url_check = URLCheck(
            url_id=id,
            h1=h1 or "",
            title=title or "",
            description=description or "",
            status_code=resp.status_code,
        )
        with get_repo() as repo:
            repo.create_url_check(url_check)
            flash("Страница успешно проверена", "success")
        return redirect(url_for("urls_show", id=id))


@app.route("/list_urls")
def get_urls_list():
    with get_repo() as repo:
        all_urls: list[URL] = repo.get_all_urls()
        latest_url_checks: dict[int, URLCheck] = {
            i.url_id: i
            for i in sorted(
                repo.get_all_checks(), key=lambda x: (x.id, x.created_at)
            )
        }
    return render_template(
        "list.html",
        urls=[
            {
                "url": url,
                "url_check": latest_url_checks.get(url.id)
                if url.id is not None
                else None,
            }
            for url in all_urls
        ],
    )  # noqa: E111
