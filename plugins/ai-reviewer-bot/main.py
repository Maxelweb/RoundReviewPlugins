from flask import Flask
from waitress import serve

from config import DEBUG, DASHBOARD_SECRET_KEY, PLUGIN_BASE_URL_PREFIX
from routes.core import core_blueprint


app = Flask(__name__)
app.secret_key = DASHBOARD_SECRET_KEY
app.register_blueprint(core_blueprint, url_prefix=PLUGIN_BASE_URL_PREFIX)


if __name__ == "__main__":
    if DEBUG:
        app.config["TEMPLATES_AUTO_RELOAD"] = True
        app.run(host="0.0.0.0", port=8083, debug=DEBUG)
    else:
        serve(app, host="0.0.0.0", port=8083)