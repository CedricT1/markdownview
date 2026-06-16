from flask import Flask


def create_app():
    app = Flask(__name__)

    # Limite la taille des requêtes (anti-DoS sur WeasyPrint / Pandoc).
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 Mo

    from . import routes
    routes.init_app(app)

    return app
