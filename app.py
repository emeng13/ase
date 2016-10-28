from flask import Flask, render_template, request
from passlib.hash import sha256_crypt

import pymssql
import Bill 
app = Flask(__name__)

conn = pymssql.connect(server='eats.database.windows.net', \
  user='th2520@eats',\
  password='123*&$eats',\
  database='AERIS')\

@app.route("/")
def main():
  cursor = conn.cursor()
  # cursor.execute("""
  #   IF OBJECT_ID('Users', 'U') IS NOT NULL
  #     DROP TABLE Users
  #   CREATE TABLE Users (
  #     FirstName VARCHAR(255) NOT NULL,
  #     LastName VARCHAR(255) NOT NULL,
  #     Email varchar(255) NOT NULL PRIMARY KEY,
  #     Password varchar(255) NOT NULL 
  #   )
  #   """)
  cursor.execute("SELECT * FROM Users")
  data = cursor.fetchall()
  print data

  
  conn.commit()

  return render_template('index.html')
 

@app.route('/login', methods=['POST'])
def login():
  email = request.form['email']
  password = request.form['password']
  cursor = conn.cursor()
  cursor.execute("SELECT password FROM Users WHERE Email=%s", email)

  if cursor.rowcount == 0: # email doesn't exist in db
    print "Sign up first!"
  else:
    data = cursor.fetchall()

    print data[0][0]
    print password 
    if sha256_crypt.verify(password, data[0][0]):
      print "You are logged in!"
    else:
      print "wrong password!"
  conn.commit()
  return render_template('index.html')


@app.route('/signUp', methods=['POST'])
def signup():
  firstName = request.form['firstName']
  lastName = request.form['lastName']
  email = request.form['email']
  password = sha256_crypt.encrypt(request.form['password'])

  # find if the email exists in the database
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM Users WHERE Email =%s", email)

  if cursor.rowcount == 0: # no existing email in db
    cursor.execute("INSERT INTO Users VALUES (%s, %s, %s, %s)", (firstName,lastName, email, password))
    conn.commit()
  else:
    print "You already have an account! Login!"
  
  return render_template('index.html')

if __name__ == "__main__":
  app.run(debug = True)