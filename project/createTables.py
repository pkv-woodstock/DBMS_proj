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
cursor.execute('''
    CREATE TABLE if not exists users (
    UserID INT PRIMARY KEY,
    Username VARCHAR(50),
    Password VARCHAR(50),
    FullName VARCHAR(100),
    Email VARCHAR(100),
    Role VARCHAR(50)
);
    CREATE TABLE if not exists projects (
    ProjectID INT PRIMARY KEY,
    ProjectName VARCHAR(255),
    Description TEXT,
    StartDate DATE,
    EndDate DATE,
    Status VARCHAR(50),
    ModifiedTimestamp TIMESTAMP NOT NULL,
    LastModifiedByUserID INT NOT NULL,
    FOREIGN KEY (LastModifiedByUserID) REFERENCES users(UserID)
);
    CREATE TABLE if not exists Collaborators (
    CollaboratorID INT PRIMARY KEY,
    JoinDate DATE,
    ProjectID INT,
    UserID INT,
    FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);
    CREATE TABLE if not exists tasks (
    TaskID INT PRIMARY KEY,
    TaskName VARCHAR(255),
    Description TEXT,
    Deadline DATE,
    Status VARCHAR(50),
    Priority INT,
    ProjectID INT,
    AssigneeID INT,
    Category VARCHAR(50),
    ModifiedTimestamp TIMESTAMP NOT NULL,
    LastModifiedByUserID INT NOT NULL,
    FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) ON DELETE CASCADE,
    FOREIGN KEY (AssigneeID) REFERENCES users(UserID),
    FOREIGN KEY (LastModifiedByUserID) REFERENCES users(UserID)
);
    CREATE TABLE if not exists comments (
    CommentID INT PRIMARY KEY,
    TaskID INT,
    UserID INT,
    CommentText TEXT,
    ModifiedTimestamp TIMESTAMP NOT NULL,
    LastModifiedByUserID INT NOT NULL,
    FOREIGN KEY (TaskID) REFERENCES tasks(TaskID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES users(UserID),
    FOREIGN KEY (LastModifiedByUserID) REFERENCES users(UserID)
);
    CREATE TABLE if not exists logs (
    LogID INT PRIMARY KEY,
    RecordID INT,
    ModifiedTimestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (RecordID) REFERENCES tasks(TaskID) ON DELETE CASCADE
);
    ''')
mysql_connection.commit()