from flask import Flask, render_template, request, redirect
from passlib.hash import sha256_crypt
from random import randint

import pymssql
app = Flask(__name__)

# server connection
conn = pymssql.connect(server='eats.database.windows.net', \
  user='th2520@eats',\
  password='123*&$eats',\
  database='AERIS')\


# global variables for current logged in user and bill session
user_email = ""
bill_id = -1



@app.route("/")
def main():
  cursor = conn.cursor()
  # create Users table
  # cursor.execute("""
    # IF OBJECT_ID('Users', 'U') IS NOT NULL
    #   DROP TABLE Users
    # CREATE TABLE Users (
    #   FirstName VARCHAR(255) NOT NULL,
    #   LastName VARCHAR(255) NOT NULL,
    #   Email varchar(255) NOT NULL PRIMARY KEY,
    #   Password varchar(255) NOT NULL 
    # )
    # """)
  cursor.execute("SELECT * FROM Users")
  data = cursor.fetchall()

  print data # debug print User table

  conn.commit()
  cursor.close()

  cursor1 = conn.cursor()
  # create Item table
  # cursor1.execute("""
  #   CREATE TABLE Items(
  #     Email varchar(255) NOT NULL, 
  #     ItemName varchar(255) NOT NULL,
  #     Quantity INT NOT NULL,
  #     Price DECIMAL(10,2) NOT NULL,     
  #     BillId INT NOT NULL,
  #     PRIMARY KEY (Email, ItemName)
  #   )
  #   """)

  conn.commit()
  cursor1.close()

  return render_template('index.html')
 


@app.route('/login', methods=['POST'])
def login():
  email = request.form['email']
  password = request.form['password']

  # set global variable for current logged in user
  global user_email 
  user_email = email

  cursor = conn.cursor()
  cursor.execute("SELECT password FROM Users WHERE Email=%s", email)

  if cursor.rowcount == 0: # email doesn't exist in Users table
    print "Sign up first!"
  else:
    data = cursor.fetchall()
    cursor.close()

    if sha256_crypt.verify(password, data[0][0]): # login OK
      
      print "Login successful!"
      return redirect('bill')
    else: # login failed
      print "Incorrect password!"
  
  cursor.close()
  return render_template('index.html')



@app.route('/signUp', methods=['POST'])
def signup():
  firstName = request.form['firstName']
  lastName = request.form['lastName']
  email = request.form['email']
  password = sha256_crypt.encrypt(request.form['password'])

  # check if email exists in Users table
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM Users WHERE Email=%s", email)

  if cursor.rowcount == 0: # email doesn't exist in Users table
    cursor.execute("INSERT INTO Users VALUES (%s, %s, %s, %s)", (firstName,lastName, email, password))
    conn.commit()
  elif cursor.rowcount > 1: # multiple emails exist in Users table
    sys.exit("ERROR: DUPLICATE EMAILS IN DATABASE")
  else: # email already exists in Users table
    print "Account exists!"
  
  cursor.close()
  return render_template('index.html')



# BILL PAGE
@app.route('/bill', methods=['GET', 'POST'])
def bill():
  # checks if table is already created, if it is, table is dropped and new table created
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

  global user_email

  # find all bills associated with user
  cursor2 = conn.cursor()
  cursor2.execute("SELECT billID, Email FROM Bill_Users WHERE Email=%s", user_email)
  data = cursor2.fetchall()

  Userbill = [dict(BillID=row[0], Email=row[1]) for row in data]

  cursor2.close()

  conn.commit()

  return render_template('bill.html', Userbill=Userbill)

# CREATE BILL
@app.route('/create_bill', methods=['GET', 'POST'])
def create_bill():

  # generate bill id
  isUnique = False
  while(isUnique == False):
    randomNum = (randint(0,1000))
    cursor1 = conn.cursor()
    result = cursor1.execute("SELECT billID FROM Bill_Users WHERE billID = %d", randomNum)
    if (randomNum != result):
      print "Created bill session!" # debug print
      isUnique = True
      cursor1.close()

  # add bill to Bill_Users table
  cursor2 = conn.cursor()
  cursor2.execute("INSERT INTO Bill_Users VALUES (%d, %s)", (randomNum, user_email))
  cursor2.close()
  
  conn.commit()
  
  return redirect('bill')



# DISPLAY BILL
@app.route('/display_bill', methods=['GET', 'POST'])
def display_bill():
  if request.method == 'POST':
    global user_email

    # set global variable for current bill session
    global bill_id
    bill_id = request.form['billId']

    # retrieve all items in Items table associated with email and bill
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items WHERE billID=%d", (bill_id))
    data = cursor.fetchall()
    cursor.close()

    Userbill = [dict(Email=row[0], ItemName=row[1], Quantity=row[2], Price=row[3]) for row in data]

    # retrieve all users in Bill_Users table associated with bill
    cursor1 = conn.cursor()
    cursor1.execute("SELECT * FROM Bill_Users WHERE billID=%d", (bill_id))
    data = cursor1.fetchall()
    cursor1.close()

    cursor2 = conn.cursor()

    Userlist = []

    # retrieve names of users in Users table associated with email
    for row in data:
      cursor.execute("SELECT * FROM Users WHERE Email=%s", row[1])
      data1 = cursor2.fetchall()
      Userdict = {}
      Userdict["Name"] = data1[0][0]
      Userdict["Email"] = row[1]
      Userlist.append(Userdict)

    conn.commit()

    # bill shows list of items
    return render_template('display_bill.html', Userbill=Userbill, Userlist=Userlist, Billid=bill_id)

# ADD ITEM
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
  if request.method == 'POST':
    global user_email
    global bill_id

    item_name = request.form['item']
    quantity = request.form['quantity']
    price = request.form['price']

    if(quantity <= 0):
      sys.exit("ERROR: QUANTITY CANNOT BE 0")

    if(price <= 0):
      sys.exit("ERROR: PRICE CANNOT BE LESS THAN $0")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO Items VALUES (%s, %s, %d, %d, %d)", (user_email, item_name, quantity, price, bill_id))
    conn.commit()

    # retrieve all items in Items table associated with email and bill
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items WHERE billID=%d", (bill_id))
    data = cursor.fetchall()
    cursor.close()

    Userbill = [dict(Email=row[0], ItemName=row[1], Quantity=row[2], Price=row[3]) for row in data]

    # retrieve all users in Bill_Users table associated with bill
    cursor1 = conn.cursor()
    cursor1.execute("SELECT * FROM Bill_Users WHERE billID=%d", (bill_id))
    data = cursor1.fetchall()
    cursor1.close()

    cursor2 = conn.cursor()

    Userlist = []

    # retrieve names of users in Users table associated with email
    for row in data:
      cursor.execute("SELECT * FROM Users WHERE Email=%s", row[1])
      data1 = cursor2.fetchall()
      Userdict = {}
      Userdict["Name"] = data1[0][0]
      Userdict["Email"] = row[1]
      Userlist.append(Userdict)

    conn.commit()

    # bill shows list of items
    return render_template('display_bill.html', Userbill=Userbill, Userlist=Userlist, Billid=bill_id)


# REMOVE ITEM
@app.route('/remove_item', methods=['GET', 'POST'])
def remove_item():
  if request.method == 'POST':
    global user_email
    global bill_id

    item_name = request.form['ItemName']

    cursor = conn.cursor()
    cursor.execute("DELETE FROM Items WHERE Email=%s AND ItemName=%s AND billID=%d", (user_email, item_name, bill_id))
    conn.commit()

    # retrieve all items in Items table associated with email and bill
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items WHERE billID=%d", (bill_id))
    data = cursor.fetchall()
    cursor.close()

    Userbill = [dict(Email=row[0], ItemName=row[1], Quantity=row[2], Price=row[3]) for row in data]

    # retrieve all users in Bill_Users table associated with bill
    cursor1 = conn.cursor()
    cursor1.execute("SELECT * FROM Bill_Users WHERE billID=%d", (bill_id))
    data = cursor1.fetchall()
    cursor1.close()

    cursor2 = conn.cursor()

    Userlist = []

    # retrieve names of users in Users table associated with email
    for row in data:
      cursor.execute("SELECT * FROM Users WHERE Email=%s", row[1])
      data1 = cursor2.fetchall()
      Userdict = {}
      Userdict["Name"] = data1[0][0]
      Userdict["Email"] = row[1]
      Userlist.append(Userdict)

    conn.commit()

    # bill shows list of items
    return render_template('display_bill.html', Userbill=Userbill, Userlist=Userlist, Billid=bill_id)



# ADD FRIEND
@app.route('/add_friend', methods=['GET', 'POST'])
def add_friend():
  if request.method == 'POST':
    global user_email
    global bill_id

    Femail = request.form['Friend_email']
    billid = request.form['Billid']

    # get user from Users table
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Email=%s", (Femail))
    data = cursor.fetchall()
    conn.commit()

    # add user into Bill_Users table
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Bill_Users VALUES (%d, %s)", (billid, Femail))
    conn.commit()

    # retrieve all items in Items table associated with email and bill
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items WHERE billID=%d", (bill_id))
    data = cursor.fetchall()
    cursor.close()

    Userbill = [dict(Email=row[0], ItemName=row[1], Quantity=row[2], Price=row[3]) for row in data]

    # retrieve all users in Bill_Users table associated with bill
    cursor1 = conn.cursor()
    cursor1.execute("SELECT * FROM Bill_Users WHERE billID=%d", (bill_id))
    data = cursor1.fetchall()
    cursor1.close()

    cursor2 = conn.cursor()

    Userlist = []

    # retrieve names of users in Users table associated with email
    for row in data:
      cursor.execute("SELECT * FROM Users WHERE Email=%s", row[1])
      data1 = cursor2.fetchall()
      Userdict = {}
      Userdict["Name"] = data1[0][0]
      Userdict["Email"] = row[1]
      Userlist.append(Userdict)

    conn.commit()

    # bill shows list of items
    return render_template('display_bill.html', Userbill=Userbill, Userlist=Userlist, Billid=bill_id)



# SPLIT COST
@app.route('/split_cost', methods=['GET', 'POST'])
def split_cost():
  if request.method == 'POST':
    global user_email
    global bill_id

    tip = float(request.form['Tip'])
    billid = request.form['Billid']
    post_tax = float(request.form['Total'])

    # retrieve all items associated with email and bill
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Items WHERE Email=%s AND billID=%d", (user_email, bill_id))
    data = cursor.fetchall()

    Userbill = [dict(Email=row[0], ItemName=row[1], Quantity=row[2], Price=row[3]) for row in data]

    pre_tax = 0.0
    user_total = 0.0
    for item in Userbill:
  	  print item
  	  if item['Email'] == user_email:
  	  	user_total += (float(item['Price']) * int(item['Quantity']))
  	  pre_tax += (float(item['Price']) * int(item['Quantity']))

    if(user_total > pre_tax):
      sys.exit("ERROR: USER BILL GREATER THAN TOTAL BILL")

    user_total = ((user_total / pre_tax) * post_tax) * (1 + tip)
    user_total = ("%.2f" % user_total)
    print user_total

    return render_template('split_cost.html', Cost = user_total)

if __name__ == "__main__":
	app.run(debug = True)