from flask_sqlalchemy import SQLAlchemy
from datamanager.data_manager_interface import DataManagerInterface
from models import Movie, User, db

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        self.db = db  # Use the db instance from models.py
        self.app = app

    def get_all_users(self):
        """
        Retrieve all users from the database
        Returns: List of user objects
        """
        try:
            users = self.db.session.query(User).all()
            return users
        except Exception as e:
            print(f"Error retrieving users: {str(e)}")
            return []
        
    def add_user(self, username):
        """
        Add a new user to the database
        Args:
            username: The username of the new user
        Returns: The created user object if successful, None if failed
        """
        try:
            print('Starting add_user with username:', username)
            new_user = User(username=username)
            self.db.session.add(new_user)
            self.db.session.commit()
            return new_user
        except Exception as e:
            self.db.session.rollback()
            return None
        
    def add_movie(self, title, director, year, rating, user_id):
        """
        Add a new movie to the database and associate it with a user
        Args:
            title: The title of the movie
            director: The director of the movie
            year: The release year
            rating: The movie rating
            user_id: The ID of the user who is adding the movie
        Returns: The created movie object if successful, None if failed
        """
        try:
            user = self.db.session.query(User).get(user_id)
            if not user:
                return None
                
            new_movie = Movie(
                title=title,
                director=director,
                year=year,
                rating=rating
            )
            self.db.session.add(new_movie)
            user.movies.append(new_movie)  # Create the many-to-many relationship
            self.db.session.commit()
            return new_movie
        except Exception as e:
            print(f"Error adding movie {title}: {str(e)}")
            self.db.session.rollback()
            return None

    def update_movie(self, movie):
        """
        Update the details of a movie in the database
        Args:
            movie: The movie object with updated details
        Returns: True if successful, False if failed
        """
        try:
            existing_movie = self.db.session.query(Movie).get(movie.id)
            if existing_movie:
                existing_movie.title = movie.title
                self.db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating movie {movie.id}: {str(e)}")
            self.db.session.rollback()
            return False

    def delete_movie(self, movie_id):
        """
        Delete a movie from the database
        Args:
            movie_id: The ID of the movie to delete
        Returns: True if successful, False if failed
        """
        try:
            movie = self.db.session.query(Movie).get(movie_id)
            if movie:
                self.db.session.delete(movie)
                self.db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting movie {movie_id}: {str(e)}")
            self.db.session.rollback()
            return False

    def get_user_movies(self, user_id):
        """
        Retrieve all movies associated with a specific user
        Args:
            user_id: The ID of the user
        Returns: List of movie objects
        """
        try:
            user = self.db.session.query(User).get(user_id)
            if user:
                return user.movies
            return []
        except Exception as e:
            print(f"Error retrieving movies for user {user_id}: {str(e)}")
            return []

    def remove_movie_from_user(self, user_id, movie_id):
        """
        Remove a movie from a user's list without deleting the movie from the database
        Args:
            user_id: The ID of the user
            movie_id: The ID of the movie to remove
        Returns: True if successful, False if failed
        """
        try:
            user = self.db.session.query(User).get(user_id)
            movie = self.db.session.query(Movie).get(movie_id)
            
            if user and movie:
                user.movies.remove(movie)
                self.db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error removing movie {movie_id} from user {user_id}: {str(e)}")
            self.db.session.rollback()
            return False
