from abc import ABC, abstractmethod

class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Get all movies for a specific user"""
        pass

    @abstractmethod
    def add_user(self, username):
        pass

    @abstractmethod
    def add_movie(self, title, user_id):
        pass

    @abstractmethod
    def update_movie(self, movie):
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        pass