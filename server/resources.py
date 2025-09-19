from flask import request, session, make_response, jsonify
from flask_restful import Resource
from config import db
from models import User, Recipe


class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "Username and password required"}, 422

        if User.query.filter_by(username=username).first():
            return {"error": "Username already taken"}, 422

        user = User(username=username)
        user.password_hash = password  # sets hashed password

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        return {"id": user.id, "username": user.username}, 201


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {}, 401

        user = User.query.get(user_id)
        if not user:
            return {}, 401

        return {"id": user.id, "username": user.username}, 200


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id
            return {"id": user.id, "username": user.username}, 200

        return {"error": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        session["user_id"] = None
        return {}, 204


class RecipeIndex(Resource):
    def get(self):
        recipes = Recipe.query.all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "instructions": r.instructions,
                "minutes_to_complete": r.minutes_to_complete,
                "user": {"id": r.user.id, "username": r.user.username},
            }
            for r in recipes
        ], 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        recipe = Recipe(
            title=data.get("title"),
            instructions=data.get("instructions"),
            minutes_to_complete=data.get("minutes_to_complete"),
            user_id=user_id,
        )

        db.session.add(recipe)
        db.session.commit()

        return {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user": {"id": recipe.user.id, "username": recipe.user.username},
        }, 201
