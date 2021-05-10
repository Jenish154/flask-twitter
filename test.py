from webapp import app,db,create_database

if __name__=='__main__':
	create_database(app=app)
	app.run(debug=False)