from flask import Flask
from flask import Flask, render_template, json, request, redirect
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from flask import session
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/QuickMovieReviews'

class user(db.Model):
	username=db.Column(db.String(50),primary_key=True)
	email=db.Column(db.String(100), unique=True)
	password=db.Column(db.String(255))
	
	def __init__(self,username,email,password):
		self.username=username
		self.email=email
	
	def __repr__(self)
		return '<User %r>' % self.username

#mysql = MySQL()
app.secret_key = 'why would I tell you my secret key?'

# MySQL configurations
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
#app.config['MYSQL_DATABASE_DB'] = 'QuickMovieReviews'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)

@app.route("/")
def main():
    return render_template('index.html')
    
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')
    
@app.route('/signUp',methods=['POST'])
def signUp():
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword'] 
    
    if _name and _email and _password:
             return "Hello"
            
            # All Good, let's call MySQL
            
            #conn = mysql.connect()
            #cursor = conn.cursor()
            #_hashed_password = generate_password_hash(_password)
            #cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            #data = cursor.fetchall()

            #if len(data) is 0:
            #    conn.commit()
            #    return json.dumps({'message':'User created successfully !'})
            #else:
            #    return json.dumps({'error':str(data[0])})
    #else:
        #return json.dumps({'html':'<span>Enter the required fields</span>'})
        
        
@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')
    
    
    
#@app.route('/validateLogin',methods=['POST'])
#def validateLogin():
    #try:
        #_username = request.form['inputEmail']
        #_password = request.form['inputPassword']
 
        # connect to mysql
 
        #con = mysql.connect()
        #cursor = con.cursor()
        
        #return str(_username)
                              
        #cursor.callproc('sp_validateLogin',(_username,))
        
        #data = cursor.fetchall()
        
        #return str(data[0][2])
        
        #if len(data)>0:                        
        #  if check_password_hash(str(data[0][2]),_password):
        #          session['user'] = data[0][0]
        #          return redirect('/userHome')
        #  else:
        #          return render_template('error.html',error = 'Incorrect Email address or Password.')
        #else:
        #          return render_template('error.html',error= 'Incorrect Email address or Password. ') 
 
    #except Exception as e:
    #    return render_template('error.html',error = str(e))
    #finally:
    #    cursor.close()
    #    con.close()

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')
              
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')
    
if __name__ == "__main__":
    app.run(debug=True) 
