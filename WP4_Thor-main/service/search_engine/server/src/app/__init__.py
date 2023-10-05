# import logging
from flask import Flask, request
from flask.json import jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flasgger import Swagger
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from pymongo import MongoClient
import hashlib
import datetime
from dotenv import load_dotenv
import os

from app import api

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    jwt = JWTManager(app)
    app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET_KEY"]
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=int(os.environ["JWT_ACCESS_TOKEN_EXPIRES"]))
    
    username = os.environ["MONGO_ROOT_USERNAME"]
    password = os.environ["MONGO_ROOT_PASSWORD"]
    server = os.environ["MONGO_SERVER"]
    port = os.environ["MONGO_PORT"]
    client = MongoClient(f'mongodb://{username}:{password}@{server}:{port}/?retryWrites=true&w=majority')
    db = client[os.environ["MONGO_DATABASE"]]
    users_collection = db["users"]
    
    CORS(app)

    app.config["SWAGGER"] = {
        "title": "IDUNN THOR API",
        "openapi": "3.0.3",
        "uiversion": 3,
    }
    swagger = Swagger(app, template_file="doc/apidocs.yml")

    @app.route("/")
    def homepage():
        return jsonify(
            {"status": "OK"})

    @app.route("/api/users", methods=["GET"])
    def get_user():
        return jsonify(
            {"status": "OK"})
        
    @app.route("/api/users", methods=["POST"])
    def register():
        new_user = request.get_json()
        new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()
        doc = users_collection.find_one({"username": new_user["username"].lower()})
        if not doc:
            users_collection.insert_one(new_user)
            return jsonify({'mesage': 'User created successfully'}), 201
        else:
            return jsonify({'message': 'Username already exists'}), 409

    @app.route("/api/login", methods=["post"])
    def login():
        login_details = request.get_json()
        user_from_db = users_collection.find_one({'username': login_details['username'].lower()})
        if user_from_db:
            encrypted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
            if encrypted_password == user_from_db['password']:
                access_token = create_access_token(identity=user_from_db['username'])
                return jsonify(access_token=access_token), 200
        return jsonify({'message': 'The username or password is incorrect'}), 401

    app.register_blueprint(api.bp)

    return app


if __name__ == "__main__":
    load_dotenv()
    app = create_app()
    app.run(host='0.0.0.0', debug=True)
