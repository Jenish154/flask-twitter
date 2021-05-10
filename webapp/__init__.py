from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app=Flask(__name__)
app.secret_key=b'hdudhdhd" usid/+$/@_'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///twitter.db'
app.config['UPLOAD_FOLDER']=app.root_path+'/static/pics'
app.config['MAX_CONTENT_LENGTH']=4*1024*1024
ALLOWED_EXTENSIONS={'png','jpg','jpeg'}

db=SQLAlchemy(app)
db.init_app(app)

login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='error'

def create_database(app):
	if not path.exists('flaskfolder/twitter.db'):
		db.create_all(app=app)
from webapp import routes