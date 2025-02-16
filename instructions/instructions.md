User and Movie Information

The MoviWeb app will keep track of different users and their favorite movies. Each user can have multiple movies, and each movie will have its own set of details.

At the very least, each User in our app should have:
A unique identifier (id)
A name (name)
Each Movie should have:
A unique identifier (id)
The movie’s name (name)
The movie’s director (director)
The year of release (year)
The rating of the movie (rating)

We need a Python class that will interface with the data. Let’s call it DataManager. This class will be responsible for reading the data source, and providing methods to manipulate the data (like adding, updating, or removing movies).
