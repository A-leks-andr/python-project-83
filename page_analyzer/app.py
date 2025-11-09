import os

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
    url_for
)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route("/")
def index():
	return "<h2>Welcome</h2>"








if __name__ == '__main__':
    app.run()