import atexit
from datetime import datetime, date
from flask import session, abort
from functools import wraps
from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from form import CommentForm
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
Bootstrap5(app)
ckeditor = CKEditor(app)

# Configure MySQL connection
db_config = {
    'host': 'localhost',
    'port': 8889,
    'user': 'root',
    'password': 'root',
    'database': 'taskforge',  # Added this line to specify the database
}

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, base_url=None)


def add_collaborator_to_project(user_id, project_id):
    try:
        cursor.execute('''
            INSERT INTO collaborators (UserID, ProjectID, JoinDate)
            VALUES (%s, %s, NOW())
        ''', (user_id, project_id))
        mysql_connection.commit()
    except Exception as e:
        print(f'Error adding collaborator to project: {e}')



def fetch_all_today_tasks_from_database(user_id):
    try:
        today = date.today()
        
        cursor.execute('''  
            SELECT DISTINCT tasks.*, projects.ProjectName, users.Username, users.Email
            FROM tasks
            INNER JOIN projects ON tasks.ProjectID = projects.ProjectID
            INNER JOIN users ON tasks.AssigneeID = users.UserID
            INNER JOIN Collaborators ON Collaborators.ProjectID = tasks.ProjectID
            WHERE (tasks.AssigneeID = %s OR Collaborators.UserID = %s)
            AND tasks.Deadline = %s
        ''', (user_id, user_id, today))
        
        tasks = cursor.fetchall()
        
        modified_tasks = [
            tuple("n/a" if val == "Default" else val for val in row)
            for row in tasks
        ]
        
        mysql_connection.commit()
        return modified_tasks
    
    except Exception as e:
        print(f'Error fetching tasks from database: {e}')
        return []

from datetime import date, timedelta

def fetch_all_week_tasks_from_database(user_id):
    try:
        today = date.today()
        in_a_week = today + timedelta(days=7)
        
        cursor.execute('''
            SELECT DISTINCT tasks.*, projects.ProjectName, users.Username, users.Email 
            FROM tasks
            INNER JOIN projects ON tasks.ProjectID = projects.ProjectID 
            INNER JOIN users ON tasks.AssigneeID = users.UserID
            INNER JOIN Collaborators ON Collaborators.ProjectID = tasks.ProjectID
            WHERE (tasks.AssigneeID = %s OR Collaborators.UserID = %s)
            AND tasks.Deadline BETWEEN %s AND %s
        ''', (user_id, user_id, today, in_a_week))
        
        tasks = cursor.fetchall()
        
        modified_tasks = [
           tuple("n/a" if val == "Default" else val for val in row)
           for row in tasks
        ]
        
        mysql_connection.commit()
        return modified_tasks

    except Exception as e:
        print(f'Error fetching tasks from database: {e}')
        return []
    
def fetch_all_tasks_from_database(user_id):
    try:
        #  Call the stored procedure
        cursor.callproc('GetUserTasks', [user_id])
        # Fetch the results
        result_sets = cursor.stored_results()
        tasks = []
        for result in result_sets:
            tasks.extend(result.fetchall())
        # Print the tasks to the terminal
        print("Printing all user created tasks fetched using stored procedure: ")
        for task in tasks:
            print(task)
        return tasks
    
        # cursor.execute('''
        #     SELECT * FROM tasks WHERE AssigneeID = %s
        # ''', (user_id,))
        # print(user_id)
        #combined tasks

        # cursor.execute('''
        #     SELECT DISTINCT tasks.*, projects.ProjectName, users.Username, users.Email 
        #     FROM tasks 
        #     INNER JOIN projects ON tasks.ProjectID = projects.ProjectID 
        #     INNER JOIN users ON tasks.AssigneeID = users.UserID 
        #     INNER JOIN Collaborators ON Collaborators.ProjectID = tasks.ProjectID 
        #     WHERE tasks.AssigneeID = %s OR Collaborators.UserID = %s
        # ''', (user_id,user_id,))

        tasks=cursor.fetchall()
        print("!!!!",tasks)
        modified_tasks = [
        tuple("n/a" if val == "Default" else val for val in row)
        for row in tasks
        ]
        print("!!!!!",modified_tasks)
        mysql_connection.commit()
        return modified_tasks
    except Exception as e:
        print(f'Error fetching tasks from database: {e}')
        return []
    
def fetch_individual_tasks_from_database(user_id):
    try:
        cursor.execute('''
            SELECT tasks.*, projects.ProjectName, users.Username, users.Email 
            FROM tasks 
            INNER JOIN projects ON tasks.ProjectID = projects.ProjectID 
            INNER JOIN users ON tasks.AssigneeID = users.UserID 
            WHERE tasks.AssigneeID = %s
        ''', (user_id,))
        individual_tasks = cursor.fetchall()

        modified_individual_tasks = [
            tuple("n/a" if val == "Default" else val for val in row)
            for row in individual_tasks
        ]
        
        mysql_connection.commit()
        return modified_individual_tasks
    except Exception as e:
        print(f'Error fetching individual tasks from database: {e}')
        return []

def fetch_shared_tasks_from_database(user_id):
    try:
        cursor.execute('''
            SELECT tasks.*, projects.ProjectName, users.Username, users.Email 
            FROM tasks 
            INNER JOIN projects ON tasks.ProjectID = projects.ProjectID 
            INNER JOIN Collaborators ON projects.ProjectID = Collaborators.ProjectID
            INNER JOIN users ON tasks.AssigneeID = users.UserID 
            WHERE Collaborators.UserID = %s
        ''', (user_id,))
        shared_tasks = cursor.fetchall()
        mysql_connection.commit()
        return shared_tasks
    except Exception as e:
        print(f'Error fetching shared tasks from database: {e}')
        return []

def update_last_modified_username(tasks):
    try:
        updated_tasks = []  # Initialize an empty list to store updated tasks
        for task in tasks:
            task_list = list(task)  # Convert the tuple to a list
            last_modified_user_id = task_list[10]  # Assuming 10th index is the user ID
            cursor.execute('''
                SELECT Username FROM users WHERE UserID = %s
            ''', (last_modified_user_id,))
            result = cursor.fetchone()
            if result:
                task_list[12] = result[0]  # Assuming 12th index is the last modified username
            else:
                task_list[12] = "Unknown"  # Handle case where user ID is not found
            updated_tasks.append(tuple(task_list))  # Convert the list back to a tuple and append to updated_tasks
        return updated_tasks  # Return the updated tasks list
    except Exception as e:
        print(f'Error updating last modified username: {e}')
        return tasks  # Return the original tasks list if an error occurs
    
def fetch_tasks_for_project(user_id, project_id):
    try:
        # cursor.execute('''
        #     SELECT * FROM tasks WHERE AssigneeID = %s AND ProjectID = %s
        # ''', (user_id, project_id,))
        # cursor.execute('''
        #     SELECT tasks.*, projects.ProjectName, users.Username, users.Email
        #     FROM tasks
        #     INNER JOIN projects ON tasks.ProjectID = projects.ProjectID
        #     INNER JOIN users ON tasks.AssigneeID = users.UserID
        #     WHERE tasks.AssigneeID = %s AND tasks.ProjectID = %s
        # ''', (user_id, project_id,))
        cursor.execute('''
            SELECT tasks.*, projects.ProjectName, users.Username, users.Email
            FROM tasks
            INNER JOIN projects ON tasks.ProjectID = projects.ProjectID
            INNER JOIN users ON tasks.AssigneeID = users.UserID
            WHERE tasks.ProjectID = %s
            ''', (project_id,))
        tasks = cursor.fetchall()
        mysql_connection.commit()
        new_tasks = update_last_modified_username(tasks)
        return new_tasks
    except Exception as e:
        print(f'Error fetching tasks from database: {e}')
        return []

def display_collaborators(project_id):
    # cursor.execute('SELECT u.Username, u.Email, c.UserID, c.ProjectID FROM Collaborators c JOIN Users u ON c.UserID = u.UserID WHERE c.ProjectID = %s',(project_id,))
    cursor.execute('''
        SELECT u.Username, u.Email, c.UserID, c.ProjectID, p.CreatedByUserID
        FROM Collaborators c
        JOIN Users u ON c.UserID = u.UserID
        JOIN projects p ON c.ProjectID = p.ProjectID
        WHERE c.ProjectID = %s
    ''', (project_id,))
    collaborators = cursor.fetchall()
    print(collaborators)
    return collaborators

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

cursor.execute("SHOW PROCEDURE STATUS WHERE Db = 'taskforge' AND Name = 'GetTasksByProject'")
result = cursor.fetchone()
if result:
    print("Stored procedure GetTasksByProject already exists.")
else:
    # Create the stored procedure
    cursor.execute('''
        CREATE PROCEDURE GetTasksByProject(IN project_id INT)
        BEGIN
            SELECT * FROM tasks WHERE ProjectID = project_id;
        END
    ''')


# Add trigger to set ModifiedTimestamp before inserting tasks
# Drop the trigger if it exists
cursor.execute("DROP TRIGGER IF EXISTS task_insert_trigger")

# Create the trigger
cursor.execute('''
    CREATE TRIGGER task_insert_trigger
    BEFORE INSERT ON tasks
    FOR EACH ROW
    BEGIN
        SET NEW.ModifiedTimestamp = NOW();
    END
''')


login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id, username, fullname, email, role):
        self.id = user_id
        self.username = username
        self.fullname = fullname
        self.email = email
        self.role = role


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != session.get('user_id'):
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function()


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
        print(user)
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
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
        # cursor.execute('SELECT * FROM users WHERE Email = %s', (email,))
        query = 'SELECT * FROM users WHERE Email = %s'
        params = (email,)
        cursor.execute(query, params)

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
        print(new_user_data)
        # cursor.execute('''
        #     INSERT INTO users (Username, Password, FullName, Email, Role)
        #         VALUES (%(username)s, %(password)s, %(name)s, %(email)s, %(role)s)
        # ''', new_user_data)
        query = '''
        INSERT INTO users (Username, Password, FullName, Email, Role)
        VALUES (%(username)s, %(password)s, %(name)s, %(email)s, %(role)s)
        '''
        cursor.execute(query, new_user_data)
        mysql_connection.commit()

        # Retrieve the user from the database
        cursor.execute('SELECT * FROM users WHERE Username = %s', (new_user_data['username'],))
        user_data = cursor.fetchone()
        print(user_data)
        # Create a user object
        new_user = User(user_data[0], user_data[1], user_data[3], user_data[4], user_data[5])
        session['user_id'] = user_data[0]
        # Log in the user
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/home')
@login_required
def home():
    user_id = session.get('user_id')
    print(user_id,"home")
    tasks=fetch_all_tasks_from_database(user_id)
    new_tasks = update_last_modified_username(tasks)
    print(tasks,"!!!!!!!!!!!!!!")
    individual_tasks = fetch_individual_tasks_from_database(user_id)
    # print(individual_tasks,"!!!!!!!!!!!!!!!!!!!!")
    shared_tasks = fetch_shared_tasks_from_database(user_id)
    # print("shared---",shared_tasks,"!!!!!!!!!!!!!!!!")
    # Fetch project names from the projects table
    # cursor.execute('SELECT * FROM projects WHERE CreatedByUserID = %s', (user_id,))
    cursor.execute('''SELECT p.*
        FROM projects p
        JOIN collaborators c ON p.ProjectID = c.ProjectID
        WHERE c.UserID = %s;''',(user_id,))
    projects = cursor.fetchall()
    print("Projects:")
    for project in projects:
        print(f"Project ID: {project[0]}, Project Name: {project[1]}")
    selected_project_id = request.args.get('project_id')
    # print("hi",tasks)
    return render_template('index.html', username=current_user.username, task_data_list=new_tasks, task_data_list_individual=individual_tasks, task_data_list_shared=shared_tasks, projects=projects,
                           selected_project_id=selected_project_id)

@app.route('/today')
def today():
    user_id = session.get('user_id')
    print(user_id,"home")
    tasks=fetch_all_today_tasks_from_database(user_id)
    new_tasks = update_last_modified_username(tasks)
    print(tasks,"!!!!!!!!!!!!!!")
    individual_tasks = fetch_individual_tasks_from_database(user_id)
    shared_tasks = fetch_shared_tasks_from_database(user_id)
    cursor.execute('''SELECT p.*
        FROM projects p
        JOIN collaborators c ON p.ProjectID = c.ProjectID
        WHERE c.UserID = %s;''',(user_id,))
    projects = cursor.fetchall()
    print("Projects:")
    for project in projects:
        print(f"Project ID: {project[0]}, Project Name: {project[1]}")
    selected_project_id = request.args.get('project_id')
    # print("hi",tasks)
    return render_template('index.html', username=current_user.username, task_data_list=new_tasks, task_data_list_individual=individual_tasks, task_data_list_shared=shared_tasks, projects=projects,
                           selected_project_id=selected_project_id)

@app.route('/week')
def week():
    user_id = session.get('user_id')
    print(user_id,"home")
    tasks=fetch_all_week_tasks_from_database(user_id)
    new_tasks = update_last_modified_username(tasks)
    print(tasks,"!!!!!!!!!!!!!!")
    individual_tasks = fetch_individual_tasks_from_database(user_id)
    shared_tasks = fetch_shared_tasks_from_database(user_id)
    cursor.execute('''SELECT p.*
        FROM projects p
        JOIN collaborators c ON p.ProjectID = c.ProjectID
        WHERE c.UserID = %s;''',(user_id,))
    projects = cursor.fetchall()
    print("Projects:")
    for project in projects:
        print(f"Project ID: {project[0]}, Project Name: {project[1]}")
    selected_project_id = request.args.get('project_id')
    # print("hi",tasks)
    return render_template('index.html', username=current_user.username, task_data_list=new_tasks, task_data_list_individual=individual_tasks, task_data_list_shared=shared_tasks, projects=projects,
                           selected_project_id=selected_project_id)


@app.route("/project/<int:project_id>", methods=["GET", "POST"])
def show_project(project_id):
    user_id = session.get('user_id')
    tasks = fetch_tasks_for_project(user_id, project_id)
    # cursor.execute('SELECT * FROM projects WHERE CreatedByUserID = %s', (user_id,))
    cursor.execute('''SELECT p.*
        FROM projects p
        JOIN collaborators c ON p.ProjectID = c.ProjectID
        WHERE c.UserID = %s;''',(user_id,))
    projects = cursor.fetchall()
    print(projects)
    cursor.execute('SELECT * FROM projects WHERE ProjectID = %s', (project_id,))
    requested_project = cursor.fetchone()
    collaborators = display_collaborators(project_id)
    print("------------------------------", requested_project)
    comment_form = CommentForm()

    if request.method == 'POST' and comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        text = comment_form.comment_text.data
        proj_id = project_id
        commenter = session.get('user_id')

        # SQL query to insert into comments
        sql_query = f"INSERT INTO  comments (ProjectID, UserID, CommentText, ModifiedTimestamp) VALUES (%s, %s, %s, NOW())"
        cursor.execute(sql_query, (proj_id, commenter, text))
        mysql_connection.commit()

    sql_query = '''
        SELECT c.*, u.Username, u.Email
        FROM comments c
        JOIN users u ON c.UserID = u.UserID
        WHERE c.ProjectID = %s
    '''
    cursor.execute(sql_query, (project_id,))
    comments = cursor.fetchall()
    return render_template("projects.html", projects=projects, task_data_list=tasks, project=requested_project,
                           form=comment_form, comments=comments, current_user=current_user,
                           username=current_user.username, collaborators=collaborators)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def close_db_connection():
    cursor.close()
    mysql_connection.close()


@app.route('/create_task', methods=['POST'])
def create_task():
    if request.method == 'POST':
        task_name = request.form.get('task_title', '')
        description = request.form.get('task_description', '')
        deadline = request.form.get('task_due_date', '')
        priority = request.form.get('task_priority', '')
        project_id = request.form.get('task_project_id', 0)
        assignee_id = session.get('user_id')
        category = request.form.get('task_category', '')  # add to form
        status = 0

        last_modified_by_user_id = session.get('user_id')  # will change when someone modifies

        variables_list = [
            ('task_name', task_name),
            ('description', description),
            ('deadline', deadline),
            ('priority', priority),
            ('project_id', project_id),
            ('assignee_id', assignee_id),
            ('category', category),
            ('status', status),
            ('modified_timestamp', "---"),
            ('last_modified_by_user_id', last_modified_by_user_id)
        ]

        # Print the list
        for variable, value in variables_list:
            print(f' here {variable}: {value}')

        # SQL query to insert task into the database
        # sql_query = f"INSERT INTO tasks (TaskName, Description, Deadline, Status, Priority, ProjectID, AssigneeID, Category, ModifiedTimestamp, LastModifiedByUserID) VALUES ('{task_name}', '{description}', '{deadline}', '{status}', '{priority}', {project_id}, {assignee_id}, '{category}', '{modified_timestamp}', {last_modified_by_user_id})"
        sql_query = f"INSERT INTO tasks (TaskName, Description, Deadline, Status, Priority, ProjectID, AssigneeID, Category, ModifiedTimestamp, LastModifiedByUserID) VALUES ('{task_name}', '{description}', '{deadline}', '{status}', '{priority}', {project_id}, {assignee_id}, '{category}', NOW(), {last_modified_by_user_id})"

        # Execute the SQL query
        cursor = mysql_connection.cursor()
        cursor.execute(sql_query)
        mysql_connection.commit()

        if int(project_id) != 1:
            return redirect(url_for('show_project', project_id=project_id))
        else:
            return redirect(url_for('home'))


@app.route('/add_collaborator', methods=['POST'])
def add_collaborator():
    collaborator_username = request.form.get('collaborator_username')
    project_id = request.form.get('project_id')

    # Fetch the userID based on the provided username

    cursor.execute('SELECT UserID FROM users WHERE Username = %s', (collaborator_username,))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        add_collaborator_to_project(user_id, project_id)
        flash('Collaborator added successfully.', 'success')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('show_project', project_id=project_id))

@app.route('/delete_collaborator', methods=['POST'])
def delete_collaborator():
    collaborator_user_id = request.form.get('collaborator_user_id')
    collaborator_project_id = request.form.get('collaborator_project_id')

    try:
        cursor.execute('''
            DELETE FROM collaborators
            WHERE UserID = %s AND ProjectID = %s
        ''', (collaborator_user_id, collaborator_project_id))
        mysql_connection.commit()
        flash('Collaborator removed successfully.', 'success')
    except Exception as e:
        print(f'Error removing collaborator from project: {e}')
        flash('Error removing collaborator from project.', 'error')

    return redirect(url_for('show_project', project_id=collaborator_project_id))


@app.route('/create_project', methods=['POST'])
def create_project():
    global cursor
    if request.method == 'POST':
        project_name = request.form.get('project_title')
        description = request.form.get('project_description')
        due_date = request.form.get('project_due_date')
        status = 0  # You may modify this based on your requirements

        # Get the current timestamp
        modified_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        project_created_by = session.get('user_id')
        print(project_created_by)

        # Check if the user exists
        cursor.execute('SELECT * FROM users WHERE UserID = %s', (project_created_by,))
        user_exists = cursor.fetchone()

        if not user_exists:
            flash('Error: User does not exist.', 'error')
            return redirect(url_for('home'))

        # Dummy user ID, replace with actual user ID
        last_modified_by_user_id = session.get('user_id')

        # SQL query to insert project into the database
        sql_query = f"INSERT INTO projects (ProjectName, Description, StartDate, EndDate, Status, ModifiedTimestamp, CreatedByUserID, LastModifiedByUserID) VALUES ('{project_name}', '{description}', NOW(), '{due_date}', {status}, '{modified_timestamp}', {project_created_by}, {last_modified_by_user_id})"

        # Execute the SQL query
        cursor = mysql_connection.cursor()
        cursor.execute(sql_query)
        mysql_connection.commit()

        return redirect(url_for('home'))


@app.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    if project_id:
        try:
            cursor.execute('DELETE FROM projects WHERE ProjectID = %s', (project_id,))
            mysql_connection.commit()
            flash('Project deleted successfully.', 'success')
        except Exception as e:
            print(f"Error deleting project: {e}")
            flash('Error deleting project.', 'error')
    else:
        flash('No project ID provided.', 'error')
        return redirect(url_for('home'))

    return redirect(url_for('home'))

@app.route('/edit_task', methods=['POST'])
def edit_task():
    task_id = request.form.get('task_id')
    modified_user = session.get('user_id')
    print(modified_user)
    task_name = request.form.get('editTaskName')
    description = request.form.get('editTaskDescription')
    category = request.form.get('editTaskCategory')
    deadline = request.form.get('task_due_date')
    priority = request.form.get('task_priority')

    update_query = "UPDATE tasks SET TaskName = %s, Description = %s, Category = %s, Deadline = %s, Priority = %s, ModifiedTimestamp = NOW(), LastModifiedByUserID = %s WHERE TaskID = %s"

    cursor = mysql_connection.cursor()
    cursor.execute(update_query, (task_name, description, category, deadline, priority, modified_user ,task_id,))
    mysql_connection.commit()
    redirect_url = request.form.get('redirect_url', url_for('home'))
    return redirect(redirect_url)
    # return redirect(url_for('home'))


@app.route('/delete_task', methods=['POST'])
def delete_task():
    task_id = request.form.get('task_id')

    if task_id:
        try:
            cursor = mysql_connection.cursor()

            delete_query = "DELETE FROM tasks WHERE taskID = %s"
            cursor.execute(delete_query, (task_id,))

            mysql_connection.commit()
            return redirect(url_for('home'))

        except Exception as e:
            print(f"Error deleting task: {e}")

    return "Invalid Request", 400  # Return an error if task_id is missing


@app.route('/edit_task_status/<int:task_id>', methods=['POST'])
@login_required
def edit_task_status(task_id):
    new_status = int(request.form.get('status'))
    redirect_url = request.form.get('redirect_url', url_for('home'))
    modified_user = session.get('user_id')

    # Update the task status in the database
    update_query = "UPDATE tasks SET Status = %s, ModifiedTimestamp = NOW(), LastModifiedByUserID = %s WHERE TaskID = %s"
    cursor.execute(update_query, (new_status, modified_user, task_id))
    mysql_connection.commit()

    return redirect(redirect_url)


# Register the function to be called on exit
atexit.register(close_db_connection)

if __name__ == "__main__":
    app.run(debug=True)
