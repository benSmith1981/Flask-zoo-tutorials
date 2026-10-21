from flask import Flask, render_template, redirect, request, url_for, session
import sqlite3 
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__) 
app.secret_key = "classroom-secret-key" 
DATABASE = "database.db"

@app.route("/") 
def index(): 
    greeting = " YeAR 2 Tlevel"
    return render_template("index.html",greeting = greeting)  
 
@app.route("/about") 
def about(): 
    return render_template("about.html")  


@app.route("/contact", methods=["GET", "POST"]) 
def contact(): 
 
    if request.method == "POST": 
 
        name = request.form["name"] 
        email = request.form["email"] 
        message = request.form["message"] 
 
        return render_template( 
            "contact.html", 
            name=name, 
            email=email, 
            message=message 
        ) 
 
    return render_template("contact.html") 
 

@app.route("/register", methods=["GET", "POST"]) 
def register():
    if request.method == "POST": 
        username = request.form["username"] 
        email = request.form["email"] 
        password = request.form["password"] 
        # Turn the password into a secure hash before storing it 
        password_hash = generate_password_hash(password) 
        
        conn = sqlite3.connect(DATABASE) 
        c = conn.cursor()

        # Does the username exist?
        c.execute("SELECT username FROM users WHERE username = ?",
        (username,))
        user = c.fetchone() 
        if user:
            conn.close()
            return render_template("register.html", error=f"{username} exists") 
        else:
            c.execute( 
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                (username, email, password_hash) 
            ) 
            conn.commit() 
        conn.close() 
        return redirect(url_for('login'))
    return render_template("register.html")  


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        c.execute(
            "SELECT username, password FROM users WHERE username = ?",
            (username,)
        )

        user = c.fetchone()
        conn.close()

        # Check the password against the stored hash
        if user and check_password_hash(user[1], password):
            session['username'] = user[0]
            return redirect(url_for('index'))

        return render_template(
            'login.html',
            error="Login details not recognised."
        )

    return render_template('login.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        booking_type = request.form['booking_type']

        allowed_types = ['Adult', 'Child', 'Student']
        if booking_type not in allowed_types:
            return "Error: please select a valid booking type."

        conn = sqlite3.connect(DATABASE)
        conn.execute("PRAGMA foreign_keys = ON")
        c = conn.cursor()        
        c.execute("SELECT id FROM users WHERE username = ?", 
                  (session['username'] ,))
        user = c.fetchone()

        user_id = 222 # user[0]
        try:
            c.execute(
                "INSERT INTO bookings (user_id, booking_type) VALUES (?, ?)",
                (user_id, booking_type)
            )
        except:
            print("Failed to insert booking")
            return render_template('booking.html', message=f"Failed to insert Booking received: {booking_type} for user ID {user_id}", bookings=[])

        c.execute("SELECT * FROM bookings WHERE user_id = ?", 
                  (user_id ,))
        bookings = c.fetchall()

        conn.commit()
        conn.close()
        return render_template('booking.html', message=f"Booking received: {booking_type} for user ID {user_id}", bookings=bookings)

    return render_template('booking.html', message="",bookings=[])


@app.route('/logout') 
def logout(): 
    session.pop('username', None) 
    return redirect(url_for('index')) 

@app.route("/education") 
def education(): 
    return render_template("education.html")  
 

def createdb():
 
    # Connect to the database 
    conn = sqlite3.connect(DATABASE) 
    
    # Create a cursor 
    c = conn.cursor() 
    
    # Create the table 
    c.execute(''' 
         CREATE TABLE IF NOT EXISTS users ( 
             id INTEGER PRIMARY KEY AUTOINCREMENT, 
             username TEXT, 
             email TEXT, 
             password TEXT 
         ) 
     ''') 
    
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        booking_type TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
 
    conn.commit() 
    conn.close()


if __name__ == "__main__": 
    createdb()
    app.run(debug=True) 