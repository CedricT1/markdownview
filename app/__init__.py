from flask import Flask

def create_app():
    app = Flask(__name__)

    # Configuration de l'application (si nécessaire)
    # app.config.from_object('config.ConfigClass')

    # Enregistrement des Blueprints (si vous en utilisez)
    # from .routes import main_bp
    # app.register_blueprint(main_bp)

    # Pour l'instant, nous allons définir les routes directement ici
    # pour simplifier, mais il est préférable d'utiliser des Blueprints
    # pour des applications plus grandes.
    from . import routes
    routes.init_app(app) # Fonction pour initialiser les routes

    return app