from random import randint
from passlib.hash import sha256_crypt
from flask import Flask, request, redirect, render_template, url_for

import pymssql

app = Flask(__name__)

conn = pymssql.connect(server='eats.database.windows.net',\
  user='th2520@eats',\
  password='123*&$eats',\
  database='AERIS')

user_email = "aw2802@barnard.edu" #####

CURRUSER = ""
CURRBILL = ""

@app.route("/")
def main():
  cursor = conn.cursor()

  # creates Users table
  cursor.execute("""
    IF OBJECT_ID('Users', 'U') IS NOT NULL
      DROP TABLE Users
    CREATE TABLE Users (
      FirstName VARCHAR(255) NOT NULL,
      LastName VARCHAR(255) NOT NULL,
      Email varchar(255) NOT NULL,
      Password varchar(255) NOT NULL,
      PRIMARY KEY(Email)
    )
    """)
  cursor.commit()

  return render_template('index.html')
 
@app.route('/signup', methods=['POST'])
def signup():
  firstName = request.form['firstName']
  lastName = request.form['lastName']
  email = request.form['email']
  password = sha256_crypt.encrypt(request.form['password'])

  # find given email in Users table
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM Users WHERE Email =%s", email)

  if cursor.rowcount == 0: # no users with given email in Users table
    cursor.execute("INSERT INTO Users VALUES (%s, %s, %s, %s)", (firstName, lastName, email, password))
    print "Sign up successful!"
    conn.commit()
  else:
    print "Email already in use!"
  
  return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
  email = request.form['email']
  password = request.form['password']

  cursor = conn.cursor()
  cursor.execute("SELECT Password FROM Users WHERE Email=%s", email)

  if cursor.rowcount == 0: # no users with given email in Users table
    print "Sign up first!"
  else:
    data = cursor.fetchall()

    print data[0][0] ##### how is data mapped out? 
    # print password ##### should password be printed?

    if sha256_crypt.verify(password, data[0][0]):
      print "Log in successful!"

      # set current session email
      global CURRUSER
      CURRUSER = email
      
      # retrieve all bills associated with email
      cursor1 = conn.cursor()
      cursor1.execute("SELECT * FROM Bill_Users WHERE Email=%s", CURRUSER)
      data1 = cursor1.fetchall()

      conn.commit()

      # after login, home shows list of bills
      return render_template('home.html', list=data1)

    else:
      print "Incorrect password!"
  
  conn.commit()
  
  return render_template('index.html')

# BILL PAGE
@app.route('/bill', methods=['GET', 'POST'])
def display_bill(billId):
  if billId != -1:
    # set current session bill
    CURRBILLID = billId

    # retrieve all items associated with email and bill
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items WHERE Email=%s AND BillId=%d", CURRUSER, CURRBILLID)
    data = cursor.fetchall()

    conn.commit()

    # bill shows list of items
    return render_template('bill.html', id=CURRBILLID, list=data)

  else:
    # create new bill page
    return render_template('create_bill.html')

@app.route('/create_bill', methods=['GET', 'POST'])
def create_bill():

  cursor = conn.cursor()

  # creates Bill_Users table
  cursor.execute("""
    IF OBJECT_ID('Bill_Users', 'U') IS NOT NULL
      DROP TABLE Bill_Users
    CREATE TABLE Bill_Users (
      Email varchar(255) NOT NULL,
      BillId INT NOT NULL,
      PRIMARY KEY (Email, BillId)
    )
    """)
  conn.commit()

  billId = request.form['billId']
  global CURRBILLID
  CURRBILLID = billID

  cursor.execute("INSERT INTO Bill_Users VALUES (%s, %d)", (CURRUSER, billId))
  conn.commit()

  print "Created bill %d" % CURRBILLID

 # creates Item table
  cursor.execute("""
    IF OBJECT_ID('Item', 'U') IS NOT NULL
      DROP TABLE Item
    CREATE TABLE Item(
      Email varchar(255) NOT NULL, 
      ItemName varchar(255) NOT NULL,
      Quantity INT NOT NULL,
      Price DECIMAL(10,2) NOT NULL,     
      BillId INT NOT NULL,
      PRIMARY KEY (Email, ItemName)
      FOREIGN KEY (Email) REFERENCES Users(Email)
      FOREIGN KEY (BillId) REFERENCES Bill_Users(BillId)
    )
    """)
  cursor.close()

  conn.commit()
  
  return render_template('bill.html', id=CURRBILLID, list=)

# ADD FRIEND
@app.route('/invite', methods=['GET', 'POST'])
def invite():
  # display data in html

  friendEmail = request.form['email']

  # get friend's info from Users table
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM Users WHERE EMAIL =%s", friendEmail)

  if cursor.rowcount == 0: # no users with email in Users table
    print "No users found"
  else:
    data = cursor.fetchall()

    # add friend's info into Bill_Users db
    global CURRBILLID
    cursor2 = conn.cursor()
    cursor2.execute("INSERT INTO Bill_Users VALUES (%s, %d)", (friendEmail, CURRBILLID))

  conn.commit()

  return render_template('bill.html')

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():

  global CURRUSER
  global CURRBILLID

  item_name = request.form['item']
  quantity = request.form['quantity']
  price = request.form['price']

  cursor.execute("INSERT INTO Items VALUES (%s, %s, %d, %f, %d)", (CURRUSER, item_name, quantity, price, CURRBILLID))
  conn.commit()



@app.route('/remove_item', methods=['GET', 'POST'])
def remove_item(item_name):

  global CURRUSER
  global CURRBILLID

  cursor.execute("DELETE FROM Items VALUES (%s, %s, %d, %f, %d)", (user_email, item_name, quantity, price, billId))
  conn.commit()



@app.route('/edit_item', methods=['GET', 'POST'])
def edit_item():

  cursor.execute("DELETE FROM Items VALUES (%s, %s, %d, %f, %d)", (user_email, item_name, quantity, price, billId))
  cursor.execute("INSERT INTO Items VALUES (%s, %s, %d, %f, %d)", (user_email, item_name, quantity, price, billId))
  conn.commit()





if __name__ == "__main__":
	app.run(debug = True)