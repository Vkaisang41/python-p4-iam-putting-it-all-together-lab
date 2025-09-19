#!/usr/bin/env python3

from random import randint, choice as rc
from faker import Faker

from app import app
from models import db, Recipe, User

fake = Faker()

with app.app_context():

    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()
    db.session.commit()

    print("Creating users...")
    users = []
    usernames = set()

    for _ in range(20):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.add(username)

        user = User(username=username)
        user.password_hash = f"{username.lower()}password"

        users.append(user)

    db.session.add_all(users)
    db.session.commit()  # commit so IDs are assigned

    print("Creating recipes...")
    recipes = []
    for _ in range(100):
        instructions = fake.paragraph(nb_sentences=8)

        recipe = Recipe(
            title=fake.sentence(),
            instructions=instructions,
            minutes_to_complete=randint(15, 90),
            user=rc(users)  # assign recipe to a random user
        )

        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()

    print("Seeding complete ✅")
