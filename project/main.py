import atexit

from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
Bootstrap5(app)

# Configure MySQL connection
db_config = {
    'host': 'localhost',
    'port': 8889,
    'user': 'root',
    'password': 'root',
    'database': 'taskforge',  # Added this line to specify the database
}

# Create MySQL Connection
mysql_connection = mysql.connector.connect(**db_config)
cursor = mysql_connection.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users 
    (
        UserID INT AUTO_INCREMENT PRIMARY KEY,
        Username VARCHAR(255) NOT NULL,
        Password VARCHAR(255) NOT NULL,
        FullName VARCHAR(255) NOT NULL,
        Email VARCHAR(255) NOT NULL UNIQUE,
        Role VARCHAR(255) NOT NULL
    ) 
''')
mysql_connection.commit()

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id, username, fullname, email, role):
        self.id = user_id
        self.username = username
        self.fullname = fullname
        self.email = email
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    user_query = 'SELECT * FROM users WHERE UserID = %s'
    cursor.execute(user_query, (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user = User(user_data[0], user_data[1], user_data[3], user_data[4], user_data[5])
        return user
    return None


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1], user[3], user[4], user[5]))
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
        user = cursor.fetchone()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        new_user_data = {
            'email': request.form.get('email'),
            'name': request.form.get('name'),
            'username': request.form.get('username'),
            'role': request.form.get('role'),
            'password': generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        }
        cursor.execute('''
            INSERT INTO users (Username, Password, FullName, Email, Role)
                VALUES (%(username)s, %(password)s, %(name)s, %(email)s, %(role)s)
        ''', new_user_data)
        mysql_connection.commit()

        # Retrieve the user from the database
        cursor.execute('SELECT * FROM users WHERE Username = %s', (new_user_data['username'],))
        user_data = cursor.fetchone()

        # Create a user object
        new_user = User(user_data[0], user_data[1], user_data[3], user_data[4], user_data[5])

        # Log in the user
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/home')
@login_required
def home():
    return render_template('index.html', username=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def close_db_connection():
    cursor.close()
    mysql_connection.close()


# Register the function to be called on exit
atexit.register(close_db_connection)

if __name__ == "__main__":
    app.run(debug=True)
