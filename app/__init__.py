from flask import Flask
from config import Config
from app.extensions import mail, db, login_manager
from dotenv import load_dotenv  

load_dotenv()  # load .env variables

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'main.login' #name of the login route

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all() #Creates database tables

    return app
