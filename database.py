import sqlite3 
 
# Connect to the database 
conn = sqlite3.connect("school.db") 
 
# Create a cursor 
c = conn.cursor() 
 
# Create the table 
# SQL commands for: CREATE TABLE, SELECT, FROM, WHERE, *, conditions
#

c.execute("""
CREATE TABLE IF NOT EXISTS Bookings (
    bookingID INTEGER PRIMARY KEY,
    bookingDate TEXT,
    totalPrice FLOAT
)
""")

c.execute(""" 
CREATE TABLE IF NOT EXISTS Users ( 
    userID INTEGER PRIMARY KEY, 
    userName TEXT, 
    password TEXT,
    bookingID TEXT,
    FOREIGN KEY (bookingID) REFERENCES Bookings(bookingID)

) 
""") 
 
# Insert some users

c.execute("""
INSERT INTO Users (userID, userName, password, bookingID)
VALUES (2, 'Alex', 'abc123', 2)
""")


# Save the changes
conn.commit()

# Get the users
c.execute("SELECT userName, password FROM Users WHERE userName LIKE A% ")

users = c.fetchall()

# Print the users
print("USERS")

for user in users:
    print(user)

# Close database
conn.close()