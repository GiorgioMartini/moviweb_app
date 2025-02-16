from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Movie
import os

# Get the absolute path to the instance folder
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

# Ensure instance folder exists
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "moviwebapp.db")}'
db.init_app(app)

with app.app_context():
    # This will create the database and all tables
    db.create_all()
    
    # Create sample users
    users = [
        User(username='john_doe'),
        User(username='jane_smith'),
        User(username='bob_wilson')
    ]

    # Add users to session
    for user in users:
        db.session.add(user)

    # Commit to get user IDs
    db.session.commit()

    # Create sample movies
    movies = [
        Movie(title='The Shawshank Redemption', director='Frank Darabont', year=1994, rating=9.3),
        Movie(title='The Godfather', director='Francis Ford Coppola', year=1972, rating=9.2),
        Movie(title='Pulp Fiction', director='Quentin Tarantino', year=1994, rating=8.9)
    ]

    # Add movies to session
    for movie in movies:
        db.session.add(movie)

    # Commit all changes
    db.session.commit()

    # Create relationships (users liking movies)
    users[0].movies.extend([movies[0], movies[1]])  # john_doe likes first two movies
    users[1].movies.append(movies[0])  # jane_smith likes first movie
    users[2].movies.extend([movies[1], movies[2]])  # bob_wilson likes second and third movies

    # Commit the relationships
    db.session.commit() 