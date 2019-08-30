from flask import Flask,redirect,url_for,render_template,request,flash
from flask_mail import Mail,Message
from random import randint
from database_database import Register, Base, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_login import LoginManager,login_user,current_user,logout_user,login_required


engine=create_engine('sqlite:///iiit.db',connect_args={'check_same_thread':False},
	echo=True)
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()

app=Flask(__name__)

login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'





app.secret_key='super_secret_key'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='jhansiranikella@gmail.com'
app.config['MAIL_PASSWORD']='AMMANANNA'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

mail=Mail(app)
otp=randint(000000,999999)

@app.route("/hello")
def demo():
	return "Hello world welcome to APSDC and Flask"

@app.route("/admin")
def admin():
	return  "hello admin"

@app.route("/student")
def student():
	return "hello student"


@app.route("/info/<name>")
def info(name):
	if name=='admin':
		return redirect(url_for('admin'))
	elif name=='student':
		return redirect(url_for('student'))
	else:
		return "no url"
 
@app.route("/demo_html")
def sample_html():
	return render_template('index.html')
	

@app.route("/person/<pname>/<int:n>/<branch>")
def per(pname,n,branch):
	return render_template('sample.html',name=pname,N=n,Branch=branch)

@app.route("/demo1_html")
def demo1_html():
	return render_template('login1.html')

@app.route("/table/<int:number>")

def table(number):
	return render_template('table.html',n=number)


@app.route("/file_upload", methods=['POST','GET'])
def file_upload():
	return render_template('file_upload.html')



@app.route("/dummy_data")
def dummy_data():
	dummy=[{"name":'tiru',"dob":'1998','org':'rgukt'},{"name":'pravalli','dob':'2000','org':'rgukt'}]
	return render_template('dummy.html',dummy=dummy)


@app.route("/success",methods=['POST','GET'])
def success():
	if request.method=='POST':
		f=request.files['file']
		f.save(f.filename)
		return render_template("files.html",file_name=f.filename)


@app.route("/email")
def email():
	return render_template('demo_email.html')

@app.route("/email_verify",methods=['POST','GET'])
def verify_email():
	email=request.form['email']
	msg=Message('One time password',sender='jhansiranikella@gmail.com',recipients=[email])
	msg.body=str(otp)
	mail.send(msg)
	return render_template('email_verify.html')

@app.route("/email_validate",methods=['POST','GET'])
def email_validate():
	user_otp=request.form['otp']
	if otp==int(user_otp):
		register=session.query(Register).all()
		flash("successfully login..........")
		return redirect(url_for('showdata',reg=register))
	flash("please check your otp")
	return render_template("email_verify.html")


@app.route("/")
def index():
	return render_template('index.html')


@app.route("/show", methods=['POST','GET'])
@login_required
def showdata():
	register=session.query(Register).all()
	return render_template('show.html',reg=register)

@app.route("/add",methods=['POST','GET'])
def adddata():
	if request.method=='POST':
		newdata=Register(name=request.form['name'],
			surname=request.form['surname'],
			email=request.form['email'],
			branch=request.form['branch'])
		session.add(newdata)
		session.commit()
		flash("successfully added new data")
		return redirect(url_for('showdata'))
	else:
		return render_template('add.html')

@app.route("/<int:register_id>/edit",methods=['POST','GET'])
def editdata(register_id):
	editeddata=session.query(Register).filter_by(id=register_id).one()
	if request.method=='POST':
		editeddata.name=request.form['name']
		editeddata.surname=request.form['surname']
		editeddata.email=request.form['email']
		editeddata.branch=request.form['branch']
		session.add(editeddata)
		session.commit()
		flash("successfully edited %s" %(editeddata.name))
		return redirect(url_for('showdata'))
	else:
		return render_template('edit.html',register=editeddata)

@app.route("/<int:register_id>/Delete",methods=['POST','GET'])
def deletedata(register_id):
	deldata=session.query(Register).filter_by(id=register_id).one()
	if request.method=='POST':
		session.delete(deldata)
		session.commit()
		flash("successfully deleted %s" %(deldata.name))
		return redirect(url_for('showdata',register_id=register_id))
	else:
		return render_template('delete.html',register=deldata)

@app.route("/yes")
def main():
	return render_template('first.html')

@app.route("/account",methods=['POST','GET'])
@login_required
def account():
	return render_template('account.html')

@app.route("/register",methods=['POST','GET'])
def register():
	if request.method=='POST':
		userdata=User(name=request.form['name'],
			email=request.form['email'],
			password=request.form['password'])
		session.add(userdata)
		session.commit()
		return redirect(url_for('index'))
	else:
		return render_template('register.html')
@login_required
@app.route("/login",methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('showdata'))
	try:
		if request.method=='POST':
			user = session.query(User).filter_by(
				email=request.form['email'],
				password=request.form['password']).first()
		

			if user:
				login_user(user)
				#next_page=request.args.get('next')
				return redirect(url_for('showdata'))
				#return redirect(next_page) if next_page else redirect(url_for('showData'))
			else:
				flash("login failed")
		else:
			return render_template('login.html',title="login")
	except Exception as e:
		flash("login failed....")
	else:
		return render_template('login.html',title="login")

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
	return session.query(User).get(int(user_id))

if __name__=='__main__':
	app.run(debug=True)
