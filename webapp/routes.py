import hashlib,os,datetime
from flask import request,redirect,url_for,render_template,flash
from flask_login import login_user,current_user,login_required,LoginManager,logout_user
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from webapp.models import User,Post
from webapp import app,db,ALLOWED_EXTENSIONS

def hash(s):
	s=s.encode('utf-8')
	s=hashlib.md5(s)
	return s.hexdigest()

def allowed(name):
		return name.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
		
@app.route('/')
def landing():
	return render_template('landing.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/register',methods=['POST','GET'])
def register():
	if request.method=='POST':
		email=request.form['email']
		name=request.form['name']
		password=request.form['password']
		c_password=request.form['confirm_password']
		user =User.query.filter_by(email=email).first()
		if user:
			flash('User already exists',category='error')
			return redirect(url_for('register'))
		elif len(name)<4:
			flash('Name is too short',category='error')
			return redirect('/register')
		elif password!=c_password:
			flash('Passwords dosen\'t match',category='error')
			return redirect(url_for('register'))
		elif name and password and email:
			print(f'{name} signed up with password {password}')
			password=hash(password)
			new_user=User(email=email,name=name,password=password)
			db.session.add(new_user)
			db.session.commit()
			flash('Account created successfully!',category='success')
			return redirect(url_for('landing'))
	return render_template('register.html')

@app.route('/login',methods=['POST','GET'])
def login():
	if request.method=='POST':
		email=request.form['email']
		password=request.form['password']
		password=hash(password)
		user=User.query.filter_by(email=email).first()
		if user:
			if password==user.password:
				flash('Logged in successfully',category='success')
				next_page=request.args.get('next')
				login_user(user,remember=True)
				return redirect(next_page) if next_page else redirect(url_for('home'))
			else:
				flash('Wrong Password. Try again',category='error')
				return redirect(url_for('login'))
		else:
			flash('No registered user',category='error')
			return redirect(url_for('login'))
	return render_template('register.html',login=True)


@app.route('/home',methods=['GET','POST'])
@login_required
def home():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	posts=Post.query.order_by(desc(Post.date)).all()
	if request.method=='POST':
		content=request.form['content']
		if content:
			post=Post(content=content,u_id=current_user.get_id())
			db.session.add(post)
			db.session.commit()
			return redirect(url_for('home'))
	return render_template('home.html',posts=posts)

@app.route('/logout')
@login_required
def logout():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	logout_user()
	return redirect(url_for('landing'))

@app.route('/profile')
@login_required
def profile():
	image=url_for('static',filename='pics/'+current_user.image)
	posts=reversed(current_user.posts)
	print(posts)
	return render_template('profile.html',image_file=image,posts=posts)

@app.route('/upload',methods=['POST','GET'])
@login_required
def upload():
	if request.method=='POST':
		if 'file' not in request.files:
			flash('No file selected','error')
			return redirect(url_for('upload'))
		pic=request.files['file']
		if pic.filename=='':
			flash('No file selected','error')
			return redirect(url_for('upload'))
		if pic and allowed(pic.filename):
			filename=secure_filename(pic.filename)
			if current_user.image!='default.jpg':
				prev=os.path.join(app.root_path,'static/pics',current_user.image)
				if os.path.exists(prev):
					os.remove(prev)
			pic.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			current_user.image=filename
			db.session.commit()
			flash('Profile uploaded successfully','success')
			return redirect(url_for('profile'))
		else:
			flash('File extension is not supported for image','error')
	return render_template('upload_pic.html')

@app.route('/update/post',methods=['POST','GET'])
@login_required
def update_post():
	if request.method=='POST':
		posts=current_user.posts
		for post in posts:
			if str(post.p_id) in request.form:
				return render_template('update_post.html',post=post)
	flash('Unauthorized acess','error')
	return redirect(url_for('home'))

@app.route('/change/content',methods=['POST','GET'])
@login_required
def change():
	if request.method=='POST':
		print(request.form)
		posts=current_user.posts
		for post in posts:
			print(post.p_id)
			if str(post.p_id) in request.form:
				content=request.form.get(str(post.p_id))
				if content:
					post.content=content
					post.date=datetime.datetime.now()
					db.session.commit()
					flash('Post updated','success')
					return redirect(url_for('profile'))
		return redirect(url_for('home'))

@app.route('/delete',methods=['POST','GET'])
@login_required
def delete_post():
	if request.method=='POST':
		posts=current_user.posts
		for post in posts:
			if str(post.p_id) in request.form:
				return render_template('delete_post.html',post=post)
	return redirect(url_for('home'))

@app.route('/delete/post',methods=['POST','GET'])
@login_required
def delete():
	if request.method=='POST':
		posts=current_user.posts
		for post in posts:
			if str(post.p_id) in request.form:
				db.session.delete(post)
				db.session.commit()
				flash('Post has been deleted','success')
				return redirect(url_for('profile'))
	return redirect(url_for('home'))

@app.route('/change/password',methods=['POST','GET'])
def reset_password():
	if request.method=='POST':
		email=request.form.get('email')
		cur_password=request.form.get('cur_password')
		pass1=request.form.get('password1')
		pass2=request.form.get('password2')
		user=User.query.filter_by(email=email).first()
		if user:
			if hash(cur_password)==user.password:
				user.password=hash(pass1)
				db.session.commit()
				flash('Password changed','success')
				return redirect(url_for('landing'))
			else:
				flash('Wrong password. Try again','error')
		else:
			flash('Email is not registered','error')
			
	return render_template('reset_password.html')
	
	