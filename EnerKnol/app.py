from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from mongoengine import *

app = Flask(__name__)
app.config['SECRET_KEY'] = "mostsecretivestkeyestkeyinthekeyworld123@oldmcdanl"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
connect('dogsarevenereal',host='mongodb://test:test@ds155278.mlab.com:55278/dogarevenereal')

class Dog(Document):
    breed = StringField(required=True, max_length=30)
    weight = IntField(required=True)
    lifespan = StringField(required = True)
    size =  StringField(required=True)
    temperament = StringField()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), nullable = False)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(30), unique = True, nullable = False)
    password = db.Column(db.String(30), nullable = False)

    def __repr__(self):
        return '<User %r>' % self.name

@app.route('/')
def root():
  if('log' in session):
      return redirect(url_for('search'))
  return render_template("home.html")

@app.route('/register', methods=["POST"])
def reg():
  data = request.form
  if(data['username'] == "" or data['password'] == "" or data['last'] == "" or data['first'] == ""):
      return render_template("home.html",msg="Please completely fill out the registration form.")
  elif(User.query.filter_by(username=data['username'],email = data['email']).first() != None):
    return render_template("home.html",msg="The username or email is already taken. Try again.")
  else:
    new_user = User(username=data['username'],first_name=data['first'],last_name=data['last'],email=data['email'],password=data['password'])
    db.session.add(new_user)
    db.session.commit()
  return render_template("home.html",msg="You have successfully registered. Please proceed to login.")

@app.route('/login',methods=["POST"])
def log():
    data = request.form
    if(data['user'] == "" or data['pass'] == ""):
        return render_template('home.html',msg="Please fill out the Login form completely")
    elif(User.query.filter_by(username=data['user'],password=data['pass']).first() != None):
        session['log'] = 'poop'
        return redirect(url_for("search"))
    return render_template("home.html",msg="Invalid Username / Password")

@app.route('/logout')
def logout():
    session.pop('log')
    return redirect(url_for('root'))

@app.route('/search')
def search():
    if('log' not in session):
        return redirect(url_for("root"))
    return render_template("search.html")

@app.route('/lookup',methods=["GET"])
def lookup():
    data = request.args
    doggies = Dog.objects(size__contains=data['keyword'])
    return render_template("search.html",dogs=doggies)

@app.route('/dog',methods=["GET"])
def breed():
    data = request.args
    dog = Dog.objects(breed=data['breed'])
    return render_template("dog.html",woof = dog[0])

if __name__ == '__main__':
    app.debug = True
    app.run()
