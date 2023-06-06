# Add the necessary imports
import mysql.connector as mysql
import os
import mysql.connector as mysql
from dotenv import load_dotenv

''' Environment Variables '''
load_dotenv('credentials.env')

# Read Database connection variables
db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']


# Connect to the db and create a cursor object
db =mysql.connect(user=db_user, password=db_pass, host=db_host)
cursor = db.cursor()
cursor.execute("CREATE DATABASE if not exists leaderboard;")
cursor.execute("USE leaderboard;")

cursor.execute("drop table if exists User;")
try:
   cursor.execute("""
   CREATE TABLE User (
      id          integer  AUTO_INCREMENT PRIMARY KEY,
      first_name     VARCHAR(100) NOT NULL,
      last_name     VARCHAR(100) NOT NULL,  
      student_id        integer NOT NULL,
      email     VARCHAR(100) NOT NULL,    
      username       VARCHAR(100) NOT NULL,
      password        VARCHAR(100) NOT NULL
       
   );
 """)
except RuntimeError as err:
   print("runtime error: {0}".format(err))


cursor.execute("drop table if exists sessions;")
try:
   cursor.execute("""
  CREATE TABLE sessions (
  session_id varchar(64) primary key,
  session_data json not null,
  user_id integer,
  created_at timestamp not null default current_timestamp
);
 """)
except RuntimeError as err:
   print("runtime error: {0}".format(err))

cursor.execute("drop table if exists comment;")
try:
   cursor.execute("""
  CREATE TABLE comment (
  id          integer  AUTO_INCREMENT PRIMARY KEY,
  team_id INT,
 content     VARCHAR(100) NOT NULL,
  owner_id  integer
);
 """)
except RuntimeError as err:
   print("runtime error: {0}".format(err))


