from flask import Flask, redirect, render_template, request, flash, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager
from models import db, User
import os
from dotenv import load_dotenv
import requests
import urllib.parse

# Load environment variables
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "moviwebapp.db")}'
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
if not app.secret_key:
    raise ValueError("No secret key set for Flask application. Set FLASK_SECRET_KEY environment variable.")

db.init_app(app)
data_manager = SQLiteDataManager(app) 

def fetch_movie_details(title, year=None):
    api_key = os.environ.get('OMDB_API_KEY')
    if not api_key:
        raise ValueError("No OMDB API key found. Set OMDB_API_KEY in .env file.")
    
    base_url = "https://www.omdbapi.com/"
    params = {
        'apikey': api_key,
        't': title
    }
    if year:
        params['y'] = year
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('Response') == 'True':
            return {
                'title': data.get('Title'),
                'director': data.get('Director'),
                'year': data.get('Year'),
                'rating': data.get('imdbRating'),
                'plot': data.get('Plot'),
                'poster': data.get('Poster')
            }
    return None

@app.route('/')
def home():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['GET'])
def add_user_page():
    return render_template('add_user.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        username = request.form['username']
        print(f"Attempting to add user: {username}")
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f'Username {username} is already taken!', 'error')
            return redirect('/add_users')
        
        # Try to add the user
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {username} has been successfully added!', 'success')
        return redirect('/add_users')
        
    except Exception as e:
        print(f"Error adding user: {str(e)}")
        db.session.rollback()
        flash('Error adding user. Please try again.', 'error')
        return redirect('/add_users')

@app.route('/users/<int:user_id>/add_movie', methods=['GET'])
def add_movie_page(user_id):
    return render_template('add_movie.html', user_id=user_id)

@app.route('/users/<int:user_id>/add_movie', methods=['POST'])
def add_movie(user_id):
    movie_name = request.form['movie']
    year = request.form.get('year')  # Make year optional
    
    # Fetch movie details from OMDB API
    movie_details = fetch_movie_details(movie_name, year)
    
    if movie_details:
        # Use the fetched details
        data_manager.add_movie(
            title=movie_details['title'],
            director=movie_details['director'],
            year=movie_details['year'],
            rating=movie_details['rating'],
            user_id=user_id
        )
        flash('Movie successfully added with OMDB data!', 'success')
        return redirect(f'/users/{user_id}')
    else:
        # Redirect to manual entry form with the movie name and year pre-filled
        flash('Movie not found in OMDB database. Please enter details manually.', 'info')
        return redirect(url_for('add_movie_manual', user_id=user_id, movie=movie_name, year=year))

@app.route('/users/<int:user_id>/add_movie_manual', methods=['GET'])
def add_movie_manual(user_id):
    movie = request.args.get('movie', '')
    year = request.args.get('year', '')
    return render_template('add_movie_manual.html', user_id=user_id, movie=movie, year=year)

@app.route('/users/<int:user_id>/add_movie_manual', methods=['POST'])
def add_movie_manual_post(user_id):
    try:
        data_manager.add_movie(
            title=request.form['movie'],
            director=request.form['director'],
            year=request.form['year'],
            rating=request.form['rating'],
            user_id=user_id
        )
        flash('Movie successfully added with manual data!', 'success')
    except Exception as e:
        flash('Error adding movie. Please try again.', 'error')
    
    return redirect(f'/users/{user_id}')

@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):
    try:
        # Remove the movie from the user's list
        if data_manager.remove_movie_from_user(user_id, movie_id):
            flash('Movie successfully removed from your list!', 'success')
        else:
            flash('Movie or user not found.', 'error')
    except Exception as e:
        flash('Error removing movie from list.', 'error')
    
    return redirect(f'/users/{user_id}')

@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = User.query.get(user_id)
    if user is None:
        return "User not found", 404

    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', movies=movies, user=user)

@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET'])
def update_movie_page(user_id, movie_id):
    user = User.query.get(user_id)
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('list_users'))
    
    # Find the movie in the user's movies
    movie = None
    for m in user.movies:
        if m.id == movie_id:
            movie = m
            break
    
    if movie is None:
        flash('Movie not found in your list.', 'error')
        return redirect(url_for('user_movies', user_id=user_id))
    
    return render_template('update_movie.html', user_id=user_id, movie=movie)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['POST'])
def update_movie_post(user_id, movie_id):
    user = User.query.get(user_id)
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('list_users'))
    
    # Find the movie in the user's movies
    movie = None
    for m in user.movies:
        if m.id == movie_id:
            movie = m
            break
    
    if movie is None:
        flash('Movie not found in your list.', 'error')
        return redirect(url_for('user_movies', user_id=user_id))
    
    try:
        # Update movie details
        movie.title = request.form['movie']
        movie.director = request.form['director']
        movie.year = request.form['year']
        movie.rating = request.form['rating']
        
        db.session.commit()
        flash('Movie successfully updated!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating movie. Please try again.', 'error')
    
    return redirect(url_for('user_movies', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)
