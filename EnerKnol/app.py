from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from mongoengine import *

import os,math
basedir = os.path.abspath(os.path.dirname(__file__))

#Initializing Flask application and configuring secret key for session and for flask_sqlalchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = "mostsecretivestkeyestkeyinthekeyworld123@oldmcdanl"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(basedir + "/data/", 'app.db')

#Creating the SQLAlchemy App
db = SQLAlchemy(app)

#mlab hosted database
connect('dogsarevenereal',host='mongodb://test:test@ds155278.mlab.com:55278/dogarevenereal')

#Document schema for Dogs
class Dog(Document):
    breed = StringField(required=True, max_length=30)
    weight = IntField(required=True)
    lifespan = StringField(required = True)
    size =  StringField(required=True)
    temperament = StringField()

#Model for Users
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

'''
Upon pressing register, will do procedural checks to make sure username doesn't already exist or email exists.
Also ensures that the registration form is completely filled out.
'''
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

'''
Ensures completion of the login form on the home page and if password and username match the ones stored in database
Once the user has been validated, a session will be created for the user to keep track of his or her login session.
'''
@app.route('/login',methods=["POST"])
def log():
    data = request.form
    if(data['user'] == "" or data['pass'] == ""):
        return render_template('home.html',msg="Please fill out the Login form completely")
    elif(User.query.filter_by(username=data['user'],password=data['pass']).first() != None):
        session['log'] = data['user']
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
    return render_template("search.html", user=session['log'])

'''
Currently

For pagination, I considered 3 scenarios (4 dogs is the default amount for any page):
1) The user chooses to go to a page beyond the number of pages, thus returning an empty array
2) The user wants to see the last page of the dogs but there are less than 4 dogs, so I return the remaining dogs.
3) The user chooses any page that contains 4 dogs.
'''
@app.route('/lookup/<page>',methods=["GET"])
def lookup(page):
    data = request.args
    key = data['keyword'].lower()
    doggies = Dog.objects(Q(size__contains=key) | Q(breed__contains=key) | Q(lifespan__contains=key))
    page = int(page)
    count = doggies.count()
    numPages = math.ceil(count / 4.0)
    print(numPages)
    if((page-1) * 4 > count): doggies = []
    elif(page * 4 > count): doggies = doggies[(page-1)*4:count]
    else: doggies = doggies[(page-1) * 4: page * 4]
    return render_template("search.html",dogs=doggies, pages=numPages, curPage=page, user=session['log'])

#Separate page for the dog breed
@app.route('/dog',methods=["GET"])
def breed():
    data = request.args
    dog = Dog.objects(breed=data['breed'])
    return render_template("dog.html",woof = dog[0])

if __name__ == '__main__':
    app.debug = True
    app.run()
