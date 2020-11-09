import random
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
db = SQLAlchemy(app)

class User(db.Model):
    """User (поля name, last_name, email, role (author, editor), state (active, inactive, deleted))"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)

class Post(db.Model):
    """Post (поля title, description, author (ссылка на таблицу User)."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))

name = ['Serega', 'Dima', 'Oleg', 'Vova', 'Sasha']
last_name = ['Ivanov', 'Salahov', 'Shevchuck', 'Korochov', 'Sapagov']
email = ['gmail.com', 'mail.ru']
role = ['author', 'editor']
state = ['active', 'inactive', 'deleted']
title = ['проект', 'международный', 'кино', 'театр', '20 века']
description = ['creating']
VALUE = 50


for el in name:
    db_name = el
    db_last_name = random.choice(last_name)
    db_email = db_last_name + '.' + el + '@' + random.choice(email)
    db_role = random.choice(role)
    db_state = random.choice(state)

    user = User(name=db_name, last_name=db_last_name, email=db_email, role=db_role, state=db_state)
    try:
        db.session.add(user)
        db.session.commit()
    except:
        print("error in user db")

for i in range(VALUE):
    db_title = random.choice(title) + " " + random.choice(title)
    db_description = description[0]
    db_author = random.randint(1, len(name))

    post = Post(title=db_title, description=db_description, author=db_author)
    try:
        db.session.add(post)
        db.session.commit()
    except:
        print("error in post db")