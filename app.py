from flask import Flask, render_template, request
from passlib.hash import sha256_crypt
from random import randint

import pymssql
app = Flask(__name__)

conn = pymssql.connect(server='eats.database.windows.net', \
  user='th2520@eats',\
  password='123*&$eats',\
  database='AERIS')\

user_email = "aw2802@barnard.edu"

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

# BILL PAGE
@app.route('/bill', methods=['GET', 'POST'])
def bill():
  randomNum = (randint(0,1000))

  #checks if table is already created, if it is, table is dropped and new table created
  # cursor = conn.cursor()
  # cursor.execute("""
  #   IF OBJECT_ID('Bill_Users', 'U') IS NOT NULL
  #     DROP TABLE Bill_Users
  #   CREATE TABLE Bill_Users (
  #     billID INT NOT NULL,
  #     Email varchar(255) NOT NULL,
  #     PRIMARY KEY (billID, Email)
  #   )
  #   """)
  # cursor.close()

 # This creates the Item table
  cursor = conn.cursor()
  cursor.execute("""
    IF OBJECT_ID('Item', 'U') IS NOT NULL
      DROP TABLE Item
    CREATE TABLE Item(
      Item_name varchar(255) NOT NULL,
      Email varchar(255) NOT NULL, 
      Quantity INT NOT NULL,
      Price DECIMAL(10,2) NOT NULL,     
      billID INT NOT NULL,
      PRIMARY KEY (Item_name, Email)
    )
    """)
  cursor.close()

  randomNum = (randint(0,1000))
  cursor1 = conn.cursor()
  cursor1.execute("INSERT INTO Bill_Users VALUES (%d, %s)", (randomNum, user_email))
  cursor1.close()

  # Printing values in the table for testing purposes
  cursor2 = conn.cursor()
  cursor2.execute("SELECT * FROM Bill_Users")
  data = cursor2.fetchall()
  print data
  
  conn.commit()
  
  return render_template('bill.html')

# DISPLAY BILL
@app.route('/display_bill', methods=['GET', 'POST'])
def display_bill():
	cursor2.execute("SELECT * FROM Bill_Users")
  	data = cursor2.fetchall()
  	# display data in html

  	# add item
  	cursor.execute("INSERT INTO Bill_Users VALUES (%s, %s, %d, %f)", (user_email, item_name, quantity, price))
    conn.commit()

  	# remove item
  	cursor.execute("DELETE FROM Bill_Users VALUES (%s, %s, %d, %f)", (user_email, item_name, quantity, price))
    conn.commit()
  	
  	# edit item

  	# split cost


if __name__ == "__main__":
	app.run(debug = True)