import sqlite3 
 
# Connect to the database 
conn = sqlite3.connect("school.db") 
 
# Create a cursor 
c = conn.cursor() 
 
# Create the table 
# SQL commands for: CREATE TABLE, SELECT, 
# FROM, WHERE, *, conditions


c.execute("""
CREATE TABLE IF NOT EXISTS Bookings (
    bookingID INTEGER PRIMARY KEY,
    bookingDate TEXT,
    totalPrice FLOAT
)
""")