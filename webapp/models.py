import datetime
from flask_login import UserMixin
from webapp import db,login_manager



class Post(db.Model):
	p_id=db.Column(db.Integer,primary_key=True)
	content=db.Column(db.String(700))
	date=db.Column(db.DateTime(timezone=True),default=datetime.datetime.now)
	u_id=db.Column(db.Integer,db.ForeignKey('user.u_id'))
	def get_id(self):
		return self.p_id

class User(db.Model,UserMixin):
	u_id=db.Column(db.Integer,primary_key=True)
	email=db.Column(db.String(150),unique=True)
	name=db.Column(db.String(70),nullable=False)
	image=db.Column(db.String(20),nullable=False,default='default.jpg')
	password=db.Column(db.String(150),nullable=False)
	posts=db.relationship('Post',backref='author',lazy=True)
	def get_id(self):
		return self.u_id


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))