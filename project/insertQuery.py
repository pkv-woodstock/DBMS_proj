import mysql.connector

db_config = {
    'host': 'localhost',
    'port': 8889,
    'user': 'root',
    'password': 'root',
}

# Create MySQL Connection
mysql_connection = mysql.connector.connect(**db_config)
cursor = mysql_connection.cursor()

cursor.execute(f'CREATE DATABASE IF NOT EXISTS taskforge')
cursor.execute(f'USE taskforge')

# Create table
# Assuming you have a MySQL cursor object called 'cursor'

# Insert into users
cursor.execute('''
INSERT INTO users (UserID, Username, Password, FullName, Email, Role)
VALUES
    (1, 'john_doe', 'password123', 'John Doe', 'john.doe@example.com', 'Tester'),
    (2, 'jane_smith', 'pass456', 'Jane Smith', 'jane.smith@example.com', 'User'),
    (3, 'bob_jackson', 'securePass', 'Bob Jackson', 'bob.jackson@example.com', 'User');
''')

# Insert into projects
cursor.execute('''
INSERT INTO projects (ProjectID, ProjectName, Description, StartDate, EndDate, Status, ModifiedTimestamp, CreatedByUserID, LastModifiedByUserID)
VALUES
    (0, 'Default', '', NOW(), NOW(), 0, NOW(), 1, 1),
    (101, 'Project A', 'Description for Project A', '2023-01-01', '2023-12-31', 0, NOW(), 1, 1),
    (102, 'Project B', 'Description for Project B', '2023-02-01', '2023-11-30', 0, NOW(), 1, 2);
''')

# Insert into tasks
cursor.execute('''
INSERT INTO tasks (TaskID, TaskName, Description, Deadline, Status, Priority, ProjectID, AssigneeID, Category, ModifiedTimestamp, LastModifiedByUserID)
VALUES
    (201, 'Task 1', 'Description for Task 1', '2023-03-15', 0, 'low', 101, 2, 'Development', NOW(), 1),
    (202, 'Task 2', 'Description for Task 2', '2023-04-30', 1, 'medium', 101, 3, 'Testing', NOW(), 2);
''')

# Insert into comments
cursor.execute('''
INSERT INTO comments (CommentID, ProjectID, UserID, CommentText, ModifiedTimestamp)
VALUES
    (301, 101, 2, 'Comment on Task 1', NOW()),
    (302, 102, 3, 'Comment on Task 2', NOW());
''')

# Insert into logs
cursor.execute('''
INSERT INTO logs (LogID, RecordID, ModifiedTimestamp)
VALUES
    (401, 201, NOW()),
    (402, 202, NOW());
''')

# Insert into Collaborators
cursor.execute('''
INSERT INTO Collaborators (CollaboratorID, JoinDate, ProjectID, UserID)
VALUES
    (501, '2023-01-15', 101, 2),
    (502, '2023-02-01', 101, 3);
''')
mysql_connection.commit()