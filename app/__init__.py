from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
    socketio.init_app(app, cors_allowed_origins=["http://localhost:5173", "http://127.0.0.1:5173"])

    from app.models import user, appointment, service, vehicle, availability
    from app.views.auth_view import auth_bp
    from app.views.service_view import service_bp
    from app.views.appointment_view import appointment_bp
    from app.views.provider_view import provider_bp
    from app.views.vehicle_view import vehicle_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(service_bp, url_prefix='/services')
    app.register_blueprint(appointment_bp, url_prefix='/appointments')
    app.register_blueprint(provider_bp, url_prefix='/providers')
    app.register_blueprint(vehicle_bp, url_prefix='/vehicles')

    from app.sockets import events

    return app
