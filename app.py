from flask import Flask
from flask import Flask, render_template, request, redirect, url_for
from werkzeug import generate_password_hash, check_password_hash
from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, FloatField, TextAreaField
from wtforms.validators import InputRequired, Email, Length
from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView
from werkzeug.exceptions import HTTPException
import flask_admin.contrib.sqla
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://movie_reviews_dev:pwd@localhost:7001/movie-reviews-db'
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class user(UserMixin, db.Model):
	id=db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(50), nullable=False)
	email=db.Column(db.String(100), unique=True, nullable=False)
	password=db.Column(db.String(255), nullable=False)
	
class movie(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(50), nullable=False)
	released_date=db.Column(db.Date, nullable=False)
	directed_by=db.Column(db.String(50))
	plot=db.Column(db.TEXT)
		
class review(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(50), nullable=False)
	desc=db.Column(db.TEXT)
	date_posted=db.Column(db.DateTime)
	movie_id=db.Column(db.Integer)
	user_id=db.Column(db.Integer)
	
			
admin=Admin(app)
admin.add_view(ModelView(user,db.session))
admin.add_view(ModelView(movie,db.session))
admin.add_view(ModelView(review,db.session))

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class AddReviewForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(),Length(max=100)])
    desc=TextAreaField('Detailed Review', validators=[InputRequired()])
    
class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

	
@app.context_processor
def my_utility_processor():
	def get_movie_name(movie_id):	
		movies = movie.query.filter_by(id=movie_id).one()
		return str(movies.name)
	def get_user_name(user_id):
		users=user.query.filter_by(id=user_id).one()
		return str(users.username)
	return dict(movie_name=get_movie_name,user_name=get_user_name)
	
    
    
@app.route("/")
def main():
	movies=movie.query.limit(5).all()
	return render_template('index.html',message="Read latest reviews real quick",movies=movies)
	
@app.route("/movies")
def movies1():
	movies=movie.query.all()
	return render_template('movies.html',movies=movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        new_user = user.query.filter_by(username=form.username.data).first()
        if new_user:
            if check_password_hash(new_user.password, form.password.data):
                login_user(new_user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template('error.html', error="Invalid username or password")
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('signin.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = user(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        movies=movie.query.limit(5).all()
        return render_template('index.html',message='Your account has been created successfully',movies=movies)
        
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)
    
@app.route('/dashboard')
@login_required
def dashboard():
    movies=movie.query.limit(5).all()
    reviews=review.query.filter_by(user_id=current_user.id).all()
    return render_template('userHome.html', name=current_user.username, reviews=reviews,movies=movies)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    movies=movie.query.limit(5).all()
    return render_template('index.html',message="You've been successfully logged out",movies=movies)  
    

@app.route('/movies/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def movies(movie_id):
    movie_post=movie.query.filter_by(id=movie_id).first()
    reviews=review.query.filter_by(movie_id=movie_id).all()
    return render_template('movie.html',movie=movie_post, reviews=reviews)
    
@app.route('/<int:movie_id>/addreview', methods=['GET', 'POST'])
@login_required
def addReview(movie_id):
	form = AddReviewForm()
	if form.validate_on_submit():
		if(db.session.query(review.query.filter(review.user_id == current_user.id, review.movie_id == movie_id).exists()).scalar()):
			return render_template('error.html', error="Your review already exists")
		else:
			new_review = review(title=form.title.data, desc=form.desc.data,movie_id=movie_id,user_id=current_user.id,date_posted=datetime.now())
			db.session.add(new_review)
			db.session.commit()
			movies=movie.query.limit(5).all()
			return render_template('index.html',message='Your review has been posted successfully',movies=movies)
	movies=movie.query.filter_by(id=movie_id).first()
	return render_template('addReview.html', form=form, movies=movies)
	
@app.route('/deletereview/<int:user_id>/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def deleteReview(user_id,movie_id):
	if(db.session.query(review.query.filter(review.user_id == user_id, review.movie_id == movie_id).exists()).scalar()):
		new_review=review.query.filter_by(user_id=user_id).filter_by(movie_id=movie_id).one()
		db.session.delete(new_review)
		db.session.commit()
		movies=movie.query.limit(5).all()
		return redirect(url_for('dashboard'))	
	return render_template('error.html', error="Something unexpected has occured")


    
if __name__ == "__main__":
    app.run(debug=True,port=80) 
