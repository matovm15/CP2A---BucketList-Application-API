import os
from flask import Flask, redirect, jsonify
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.auth import auth
from src.buckets import buckets
from src.database import db, Bucket
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from flask_migrate import Migrate




def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/db",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
            SWAGGER={
                'title': "CP2A - BucketList Application API",
                'uiversions': 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)
    migrate = Migrate(app,db)
    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(buckets)
    Swagger(app, config=swagger_config, template=template)


    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handler_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handler_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR
    return app


