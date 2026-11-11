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
 
    # Check that the user is logged in 
    if 'username' not in session: 
        return redirect(url_for('login')) 
 
    # Connect to database 
    conn = sqlite3.connect(DATABASE) 
    conn.row_factory = sqlite3.Row 
 
    c = conn.cursor() 
 
    # Find the current user's ID 
    c.execute( 
        "SELECT id FROM users WHERE username = ?", 
        (session['username'],) 
    ) 
 
    user = c.fetchone() 
 
    if user is None: 
        conn.close() 
        return redirect(url_for('login')) 
 
    user_id = user['id'] 
 
    # If the form has been submitted 
    if request.method == 'POST': 
 
        ticket_id = request.form['ticket_id'] 
        quantity = request.form['quantity'] 
 
        # Validate the quantity 
        try: 
            ticket_id = int(ticket_id) 
            quantity = int(quantity) 
        except (ValueError, TypeError): 
            conn.close() 
            return "Invalid ticket or quantity." 
 
        if quantity < 1 or quantity > 20: 
            conn.close() 
            return render_template( 
                'booking.html', 
                message="Please select between 1 and 20 tickets."  
            ) 
 
        # Get the ticket price from the database 
        c.execute(""" 
            SELECT ticket_name, price 
            FROM TicketTypes 
            WHERE ticket_id = ? 
        """, (ticket_id,)) 
 
        ticket = c.fetchone() 
 
        if ticket is None: 
            conn.close() 
            return render_template( 
                'booking.html', 
                message= "Invalid ticket type."  
            ) 
 
        # Calculate total price 
        unit_price = ticket['price'] 
 
        total_price = unit_price * quantity 
 
        # Save booking to database 
        c.execute(""" 
            INSERT INTO Bookings 
            (user_id, ticket_id, quantity, 
             unit_price, total_price, status) 
            VALUES (?, ?, ?, ?, ?, 'Pending') 
        """, ( 
            user_id, 
            ticket_id, 
            quantity, 
            unit_price, 
            total_price 
        )) 
 
        # Get the ID of the new booking 
        booking_id = c.lastrowid 
 
        # Save database changes 
        conn.commit() 
 
        # Close connection 
        conn.close() 
 
        # Redirect to summary page 
        return redirect( 
            url_for('booking_summary', booking_id=booking_id) 
        ) 
 
    # GET request: retrieve ticket types 
    c.execute("SELECT * FROM TicketTypes") 
 
    tickets = c.fetchall() 
 
    conn.close() 
 
    return render_template( 
        'booking.html', 
        tickets=tickets 
    )

@app.route('/booking-summary/<int:booking_id>') 
def booking_summary(booking_id): 
 
    # Check user is logged in 
    if 'username' not in session: 
        return redirect(url_for('login')) 
 
    # Connect to database 
    conn = sqlite3.connect(DATABASE) 
    conn.row_factory = sqlite3.Row 
 
    c = conn.cursor() 
 
    # Retrieve booking and ticket information 
    c.execute(""" 
        SELECT 
            Bookings.booking_id, 
            Bookings.quantity, 
            Bookings.unit_price, 
            Bookings.total_price, 
            Bookings.status, 
            TicketTypes.ticket_name 
 
        FROM Bookings 
 
        JOIN TicketTypes 
        ON Bookings.ticket_id = TicketTypes.ticket_id 
 
        JOIN users 
        ON Bookings.user_id = users.id 
 
        WHERE Bookings.booking_id = ? 
        AND users.username = ? 
 
    """, (booking_id, session['username'])) 
 
    booking = c.fetchone() 
 
    conn.close() 
 
    # Check booking exists 
    if booking is None: 
        return "Booking not found." 
 
    return render_template( 
        'booking_summary.html', 
        booking=booking 
    )  

@app.route('/pay/<int:booking_id>', methods=['POST']) 
def pay(booking_id): 
 
    # Check user is logged in 
    if 'username' not in session: 
        return redirect(url_for('login')) 
 
    # Connect to database 
    conn = sqlite3.connect(DATABASE) 
    conn.row_factory = sqlite3.Row 
 
    c = conn.cursor() 
 
    # Check that the booking belongs to this user 
    c.execute(""" 
        SELECT Bookings.booking_id, 
               Bookings.total_price, 
               Bookings.status 
 
        FROM Bookings 
 
        JOIN users 
        ON Bookings.user_id = users.id 
 
        WHERE Bookings.booking_id = ? 
        AND users.username = ? 
 
    """, (booking_id, session['username'])) 
 
    booking = c.fetchone() 
 
    if booking is None: 
        conn.close() 
        return "Booking not found." 
 
    # Only allow pending bookings to be paid 
    if booking['status'] != 'Pending': 
        conn.close() 
        return "This booking has already been processed." 
 
    # Update booking status 
    c.execute(""" 
        UPDATE Bookings 
        SET status = 'Paid' 
        WHERE booking_id = ? 
    """, (booking_id,)) 
 
    # Save changes 
    conn.commit() 
 
    conn.close() 
 
    # Display confirmation page 
    return render_template( 
        'confirmation.html', 
        booking_id=booking_id 
    ) 

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
 
    # Enable foreign keys 
    conn.execute("PRAGMA foreign_keys = ON") 
 
    # Create a cursor 
    c = conn.cursor() 
 
    # Create Users table 
    c.execute(""" 
        CREATE TABLE IF NOT EXISTS users ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT, 
            email TEXT, 
            password TEXT 
        ) 
    """) 
 
    # Create TicketTypes table 
    c.execute(""" 
        CREATE TABLE IF NOT EXISTS TicketTypes ( 
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            ticket_name TEXT NOT NULL, 
            price REAL NOT NULL 
        ) 
    """) 
 
    # Create Bookings table 
    c.execute(""" 
        CREATE TABLE IF NOT EXISTS Bookings ( 
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER NOT NULL, 
            ticket_id INTEGER NOT NULL, 
            quantity INTEGER NOT NULL, 
            unit_price REAL NOT NULL, 
            total_price REAL NOT NULL, 
            booking_date TEXT DEFAULT CURRENT_TIMESTAMP, 
            status TEXT DEFAULT 'Pending', 
 
            FOREIGN KEY (user_id) REFERENCES users(id), 
            FOREIGN KEY (ticket_id) REFERENCES TicketTypes(ticket_id) 
        ) 
    """) 
 
    # Insert ticket types if they do not already exist 
    c.execute(""" 
        INSERT OR IGNORE INTO TicketTypes 
        (ticket_id, ticket_name, price) 
        VALUES 
        (1, 'Adult', 18.00), 
        (2, 'Child', 12.00), 
        (3, 'Student', 14.00) 
    """) 
 
    # Save changes 
    conn.commit() 
 
    # Close database 
    conn.close() 


if __name__ == "__main__": 
    createdb()
    app.run(debug=True) 