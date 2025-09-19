#!/usr/bin/env python3

from flask import Flask, request, session
from flask_restful import Api, Resource
from flask_migrate import Migrate

from models import db, User, Recipe

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "super-secret-key"

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


# ---------------- Signup ----------------
class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")
        bio = data.get("bio")
        image_url = data.get("image_url")

        if not username or not password:
            return {"error": "Invalid input"}, 422

        if User.query.filter_by(username=username).first():
            return {"error": "Username already exists"}, 422

        user = User(
            username=username,
            bio=bio,
            image_url=image_url
        )
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id

        return user.to_dict(), 201


# ---------------- CheckSession ----------------
class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = User.query.get(user_id)
        if not user:
            return {"error": "Unauthorized"}, 401

        return user.to_dict(), 200


# ---------------- Login ----------------
class Login(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401


# ---------------- Logout ----------------
class Logout(Resource):
    def delete(self):
        if "user_id" not in session or session["user_id"] is None:
            return {"error": "Unauthorized"}, 401

        session.pop("user_id", None)
        return {}, 204


# ---------------- RecipeIndex ----------------
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = User.query.get(user_id)
        if not user:
            return {"error": "Unauthorized"}, 401

        recipes = [recipe.to_dict() for recipe in user.recipes]
        return recipes, 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        title = data.get("title")
        instructions = data.get("instructions")
        minutes_to_complete = data.get("minutes_to_complete")

        if not title or not instructions or len(instructions) < 50:
            return {"error": "Invalid input"}, 422

        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user_id
        )

        db.session.add(recipe)
        db.session.commit()

        return recipe.to_dict(), 201


# Register routes
api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
